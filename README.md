# OpenRec SDK

[![CI](https://github.com/open-rec/sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/open-rec/sdk/actions/workflows/ci.yml)
![Java](https://img.shields.io/badge/Java-8-ED8B00?logo=openjdk&logoColor=white)
![Go](https://img.shields.io/badge/Go-1.20+-00ADD8?logo=go&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)

Client libraries for the [OpenRec rec-server](https://github.com/open-rec/rec-server) HTTP API.
All clients support batched user, item, and event pushes as well as legacy item, typed item, and
typed user recommendations.

| Client | Runtime | Package |
|---|---|---|
| [java-client](java-client) | Java 8 | `com.openrec:rec-client:1.0-SNAPSHOT` |
| [go-client](go-client) | Go 1.20+ | `github.com/open-rec/sdk/go-client` |
| [python-client](python-client) | Python 3.9+ | distribution `openrec-client`, import `openrec` |

## API mapping

| Operation | HTTP path | Java | Go | Python |
|---|---|---|---|---|
| Push items | `/api/push/item` | `pushItems` | `PushItems` | `push_items` |
| Push users | `/api/push/user` | `pushUsers` | `PushUsers` | `push_users` |
| Push events | `/api/push/event` | `pushEvents` | `PushEvents` | `push_events` |
| Legacy item recommend | `/api/recommend` | `recommend` | `Recommend` | `recommend` |
| Item recommend | `/api/recommend/item` | `recommendItems` | `RecommendItems` | `recommend_items` |
| User recommend | `/api/recommend/user` | `recommendUsers` | `RecommendUsers` | `recommend_users` |

New integrations should use the typed item or user recommendation methods. The legacy endpoint is
kept for compatibility. Push requests default to `INSERT`; `INSERT` and `UPDATE` are upserts.
User/item `DELETE` removes entities by ID. Events are append-only and do not support deletion.

Every convenience method generates a request ID. Java also accepts `JsonReq<T>` overloads, Go has
`WithRequest` variants, and Python has `_request` variants or a `request_id=` argument for supplying
a trace ID explicitly.

## Java client

`java-client` depends on `rec-proto` from the `rec-server` repository. Install that artifact before
building the client:

```shell
cd rec-server
mvn clean install -DskipTests
cd ../sdk/java-client
mvn clean install
```

Add the installed client to a Maven project:

```xml
<dependency>
    <groupId>com.openrec</groupId>
    <artifactId>rec-client</artifactId>
    <version>1.0-SNAPSHOT</version>
</dependency>
```

### Push and recommend

```java
RecClient client = new RecClient("http://localhost:13579");

Item item = new Item();
item.setId("item-1");
item.setScene("home");
item.setStatus(1);

ItemReq push = new ItemReq();
push.setCmd(PushCmd.INSERT);
push.setData(Collections.singletonList(item));
JsonRes<String> pushRes = client.pushItems(push);

RecommendReq recommend = new RecommendReq();
recommend.setUserId("user-1");
recommend.setScene("home");
recommend.setSize(10);
JsonRes<RecommendRes<Item>> recRes = client.recommendItems(recommend);

if (recRes != null && recRes.getCode() == ProtoCode.SUCCESS) {
    List<ScoreResult> results = recRes.getData().getResults();
}
```

Use `pushUsers` and `pushEvents` with `UserReq` and `EventReq`. Use `recommendUsers` when the target
is a user. Setting `debug=true` returns full entities in `detailInfos`, at the cost of additional
serving lookups. `itemIds` can provide explicit item triggers.

## Go client

```shell
go get github.com/open-rec/sdk/go-client
```

### Push and recommend

```go
package main

import (
    "context"
    "log"

    openrec "github.com/open-rec/sdk/go-client"
)

func main() {
    ctx := context.Background()
    client := openrec.NewClient("http://localhost:13579")

    pushRes, err := client.PushItems(ctx, openrec.ItemRequest{
        Cmd: openrec.PushInsert,
        Data: []openrec.Item{{ID: "item-1", Scene: "home", Status: 1}},
    })
    if err != nil {
        log.Fatal(err)
    }

    recRes, err := client.RecommendItems(ctx, openrec.RecommendRequest{
        UserID: "user-1",
        Scene:  "home",
        Size:   10,
    })
    if err != nil {
        log.Fatal(err)
    }
    if pushRes != nil && recRes != nil && recRes.Code == openrec.CodeSuccess && recRes.Data != nil {
        log.Printf("results: %+v", recRes.Data.Results)
    }
}
```

`NewClientWithHTTPClient` accepts a custom `http.Client` for timeouts, tracing, transports, and
retry policies. Use `PushUsers`, `PushEvents`, or `RecommendUsers` for the corresponding types.

## Python client

Install from the SDK checkout:

```shell
python -m pip install ./python-client
```

### Push and recommend

```python
from openrec import (
    CODE_SUCCESS,
    Item,
    ItemRequest,
    PushCmd,
    RecClient,
    RecommendRequest,
)

client = RecClient("http://localhost:13579", timeout=5)

push_res = client.push_items(
    ItemRequest(
        cmd=PushCmd.INSERT,
        data=[Item(id="item-1", scene="home", status=1)],
    )
)

rec_res = client.recommend_items(
    RecommendRequest(user_id="user-1", scene="home", size=10)
)
if rec_res is not None and rec_res.code == CODE_SUCCESS and rec_res.data is not None:
    print(rec_res.data.results)
```

Use `push_users`, `push_events`, or `recommend_users` for the corresponding types. The Python
runtime has no third-party dependencies; a custom `urllib` opener may be passed to `RecClient`.

## Error handling

All clients return a null/nil/`None` response for non-2xx HTTP status codes. Check both the response
and its protocol `code` before reading `data`.

- Java wraps transport failures in `RuntimeException`.
- Go returns transport and JSON failures as `error`.
- Python raises transport and JSON decoding exceptions.

There is no built-in retry policy. Configure retries and timeouts through the language-specific
HTTP client where available.

## Development

Run commands from the client directory they belong to:

```shell
# Java: Alibaba-style Eclipse formatter through Java 8-compatible Spotless
cd java-client
mvn spotless:apply
mvn spotless:check
mvn test

# Go: standard Go formatting, analysis, and tests
cd ../go-client
gofmt -w .
go vet ./...
go test ./...

# Python: PEP 8 linting/formatting and standard-library tests
cd ../python-client
python -m pip install -e ".[dev]"
ruff check .
ruff format .
python -m unittest discover -s tests -v
```

CI checks formatting and runs tests without requiring a live rec-server. For an end-to-end check,
start the standalone example and point a client at `http://localhost:13579`.
