# sdk

Client libraries for [rec-server](https://github.com/open-rec/rec-server).

| Module | Language | Artifact |
|---|---|---|
| [java-client](java-client) | Java 8 | `com.openrec:rec-client` |

## java-client

A thin OkHttp wrapper over the server's HTTP API. It handles JSON (Gson), the `JsonReq` / `JsonRes`
envelopes and the generic response types, so you work with the POJOs from `rec-proto` directly.

### build

`rec-client` depends on `rec-proto`, which comes from the `rec-server` repo — build that first or the
dependency will not resolve:

```shell
git clone https://github.com/open-rec/rec-server.git
cd rec-server && mvn clean install -DskipTests
cd ..

cd sdk/java-client && mvn clean install -DskipTests
```

```xml
<dependency>
    <groupId>com.openrec</groupId>
    <artifactId>rec-client</artifactId>
    <version>1.0-SNAPSHOT</version>
</dependency>
```

### usage

The constructor takes the server's base URL; paths (`/api/recommend`, `/api/push/*`) are appended for
you:

```java
RecClient recClient = new RecClient("http://localhost:13579");
```

One instance is enough — it holds a single `OkHttpClient`, which is thread-safe and pools connections.

#### push

Every push takes a command plus a batch, so one call can carry many rows. `INSERT` and `UPDATE` are
both upserts server-side; `DELETE` removes by id.

```java
ItemReq itemReq = new ItemReq();
itemReq.setCmd(PushCmd.INSERT);
List<Item> batchItems = new ArrayList<>();
Item item = new Item();
item.setId("item-test");
item.setCategory("category-1");
item.setScene("scene-1");
item.setStatus(1);
item.setTitle("title-test");
item.setTags("tags-1,tags-2");
item.setPubTime(String.valueOf(System.currentTimeMillis() / 1000));
batchItems.add(item);
itemReq.setData(batchItems);

JsonRes<String> jsonRes = recClient.pushItems(itemReq);
```

`pushUsers(UserReq)` and `pushEvents(EventReq)` follow the same shape.

Events are what drive recall quality: `click` events become the triggers for i2i and embedding recall,
and `expose` events feed the exposure filter.

```java
EventReq eventReq = new EventReq();
eventReq.setCmd(PushCmd.INSERT);
Event event = new Event();
event.setUserId("user-9527");
event.setItemId("item-test");
event.setScene("scene-1");
event.setType("click");
event.setValue("1");
event.setTime(String.valueOf(System.currentTimeMillis() / 1000));
eventReq.setData(Collections.singletonList(event));

recClient.pushEvents(eventReq);
```

#### recommend

```java
RecommendReq recommendReq = new RecommendReq();
recommendReq.setDeviceId("12323-545-14fffe");
recommendReq.setScene("scene-1");
recommendReq.setSize(3);
recommendReq.setUserId("user-9527");

JsonRes<RecommendRes<Item>> jsonRes = recClient.recommend(recommendReq);
List<ScoreResult> results = jsonRes.getData().getResults();
```

`recommend(...)` remains compatible with `/api/recommend`. New integrations should use
`recommendItems(...)` for `/api/recommend/item`. The SDK reserves `recommendUsers(...)` and its
`RecommendRes<User>` response type, but the server currently returns code 501 for that endpoint:

```java
JsonRes<RecommendRes<User>> jsonRes = recClient.recommendUsers(recommendReq);
```

`results` holds ids and scores in final order. Set `recommendReq.setDebug(true)` to also get
`getDetailInfos()` populated with the full `Item` objects — useful while integrating, but it costs an
extra Redis round trip per request.

Pass `setItemIds(...)` to add explicit triggers, e.g. the item currently being viewed on a
related-items page.

### correlating logs

Each call wraps your payload in a `JsonReq` with a generated `requestId`. The server puts it into its
logging MDC, so every server-side line for that request carries it. To use your own trace id, build
the envelope yourself — every method has an overload taking `JsonReq<T>`:

```java
JsonReq<RecommendReq> req = new JsonReq<>(recommendReq);
req.setRequestId(myTraceId);
JsonRes<RecommendRes<Item>> res = recClient.recommend(req);
```

### error handling

Non-2xx responses yield a **null** `JsonRes` rather than an exception, and transport failures are
rethrown as `RuntimeException`. So check for null before reading, and inspect `getCode()`
(`ProtoCode`: 200 / 400 / 404 / 500 / 504) on the result:

```java
JsonRes<RecommendRes<Item>> res = recClient.recommend(recommendReq);
if (res == null || res.getCode() != ProtoCode.SUCCESS) {
    // fall back to a default list
}
```

There is no built-in retry or timeout override; supply your own `OkHttpClient` policy by wrapping the
client if you need one.

### more examples

See `RecClientTest` in `java-client/src/test`. It expects a `rec-server` running on
`http://localhost:13579` — start one as described in
[example_standalone](https://github.com/open-rec/example/tree/master/example_standalone).
