# OpenRec SDK

[Release v0.1.0](RELEASE_NOTES.md) · [Changelog](CHANGELOG.md)

[![CI](https://github.com/open-rec/sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/open-rec/sdk/actions/workflows/ci.yml)
![JDK](https://img.shields.io/badge/JDK-21-ED8B00?logo=openjdk&logoColor=white)
![Go](https://img.shields.io/badge/Go-1.20+-00ADD8?logo=go&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)

Client libraries for the [OpenRec rec-server](https://github.com/open-rec/rec-server) HTTP API.
All clients support batched user, item, and event pushes as well as legacy item, typed item, and
typed user recommendations.

| Client | Runtime | Package |
|---|---|---|
| [java-client](java-client) | JDK 21 | `com.openrec:rec-client:0.1.0` |
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
User/item `DELETE` removes entities by ID. Event deletion differs by deployment mode:
standalone accepts `EventRequest` / `EventReq` with `cmd=DELETE` and removes the specified
item IDs from the user/scene/event-type Redis sorted set. This is serving-state cleanup, not
deleting individual historical events by event ID, and it does not clear an entire event set.
Cluster rejects event `DELETE` through the public push API. Streaming support for historical
event tombstones does not make that public operation available. The SDK enum can express
`DELETE`; callers must respect the selected mode and check the response.

Every convenience method generates a request ID. Java also accepts `JsonReq<T>` overloads, Go has
`WithRequest` variants, and Python has `_request` variants or a `request_id=` argument for supplying
a trace ID explicitly.

## Java client

The Java SDK requires JDK 21 for building and Java 21 or newer at runtime. Its `rec-proto`
dependency also targets Java 21. Older Java runtimes are no longer supported.

`java-client` depends on `rec-proto` from the `rec-server` repository. Install that artifact before
building the client:

```shell
cd rec-server
mvn clean install -DskipTests
cd ../sdk/java-client
mvn clean install
```

For SDK-only development and CI, `java-client/build-support/rec-proto-pom.xml` builds the
protocol directly without loading the rec-server parent POM. With sibling `sdk/` and
`rec-server/` checkouts, run from the SDK root using JDK 21:

```shell
mvn -f java-client/build-support/rec-proto-pom.xml install -DskipTests
mvn -f java-client/pom.xml test
```

Add the installed client to a Maven project:

```xml
<dependency>
    <groupId>com.openrec</groupId>
    <artifactId>rec-client</artifactId>
    <version>0.1.0</version>
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
serving lookups. With the matching Java 21 `rec-proto`, it also exposes
`getRecallDiagnostics()` on `RecommendRes`: node, channel, status and candidate count before
filtering/ranking/truncation. Final-result `recallScores` describes only the selected items;
it cannot establish whether every recall channel supplied candidates. Go exposes the same
diagnostics as `RecallDiagnostics`; Python exposes them as
`recall_diagnostics`. `itemIds` can provide explicit item triggers.

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

All clients report non-2xx HTTP responses as errors and preserve at most 1024 bytes of response detail:

- Java throws `RecClientHttpException`, exposing `getStatusCode()` and at most 1024 bytes from
  `getResponseBody()`. Response bodies are closed on success and failure; HTTP errors do not
  return `null`. Transport failures retain their cause in a `RuntimeException`.
- Go returns a nil response and an `*HTTPError` with `StatusCode` and `ResponseBody`;
  use `errors.As` to inspect it. Transport and JSON failures also return an `error`.
- Python raises `RecClientHttpException` with `status_code` and `response_body`.
  Transport and JSON decoding failures also raise exceptions.

For successful HTTP responses, check the protocol `code` and `status` before reading `data`.
rec-server returns HTTP 503 while the selected recommendation graph is unready. A running process
or successful `/health` response does not imply recommendation availability: deployment automation
must configure representative warmup samples and wait for `/ready`. Push/query APIs remain usable
while recommendation traffic is gated. See the server's
[readiness guide](https://github.com/open-rec/rec-server#recommendation-readiness).

There is no built-in retry policy. Configure retries and timeouts through the language-specific
HTTP client where available.

Java accepts a public `RecClient(String endpoint, OkHttpClient client)` constructor for custom
HTTP timeouts, interceptors, and transports. All clients normalize trailing slashes in endpoints.

**Migration:** Go callers that previously checked only for a nil response must now handle the
returned HTTP error. Python callers that previously checked for `None` must catch
`RecClientHttpException`. Business failures inside HTTP 2xx responses still use `code`/`status`.

## Development

Java is the reference SDK contract. All three clients consume `testdata/recommend.json` in their
tests to verify diagnostics, nullable scores, typed details, and tolerance of unknown fields.

Formatting is enforced in CI: Java uses Spotless with the Alibaba Eclipse profile; Python uses
Ruff with PEP 8 E/W checks, four-space indentation and a 79-character line limit; Go uses standard
`gofmt` and `go vet`. `.editorconfig` supplies matching editor defaults. With Java 21, Maven,
Go and Ruff on PATH, `make format`, `make format-check`, and `make test` run the common tasks.

Run commands from the client directory they belong to:

```shell
# Java: Alibaba-style Eclipse formatter through Spotless on JDK 21
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

Push retries require care: a failed batch may already have delivered some messages.
