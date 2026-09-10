# OpenRec Python client

Python 3.9+ client for the OpenRec `rec-server` HTTP API.

```shell
pip install -e .
```

```python
from openrec import RecClient, RecommendRequest

client = RecClient("http://localhost:13579", timeout=5)
response = client.recommend_items(
    RecommendRequest(user_id="user-9527", scene="scene-1", size=3)
)
if response is not None and response.status and response.data is not None:
    print(response.data.results)
```

The client provides `push_items`, `push_users`, `push_events`, `recommend`, `recommend_items`, and
`recommend_users`. Pass `request_id=` to the convenience methods or use their `_request` variants
with `JsonRequest` when a caller-supplied trace ID is required.

Non-2xx responses return `None`, matching `java-client`. Transport and JSON decoding failures are
raised to the caller. The implementation uses only the Python standard library.
