import io
import json
import unittest
from urllib.error import HTTPError, URLError

from openrec import (
    Event,
    EventRequest,
    Item,
    ItemRequest,
    JsonRequest,
    PushCmd,
    RecClient,
    RecommendRequest,
    User,
    UserRequest,
)


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()


class Opener:
    def __init__(self):
        self.requests = []

    def open(self, request, timeout=None):
        self.requests.append((request, timeout))
        if request.full_url.endswith("/api/recommend/user"):
            details = [{"id": "u2", "deviceId": "d2"}]
        elif "/api/recommend" in request.full_url:
            details = [{"id": "i2", "pubTime": "123"}]
        else:
            return Response(b'{"code":200,"status":true,"msg":"","data":"ok"}')
        body = {
            "code": 200,
            "status": True,
            "msg": "",
            "data": {
                "results": [{"id": "i2", "score": 1.5, "rankScore": 0.8}],
                "detailInfos": details,
            },
        }
        return Response(json.dumps(body).encode())


class RecClientTest(unittest.TestCase):
    def test_paths_payloads_and_typed_responses(self):
        opener = Opener()
        client = RecClient("http://openrec.test/", opener=opener, timeout=2)

        self.assertTrue(
            client.push_items(
                ItemRequest(data=[Item(id="i1", pub_time="123", ext_fields={"x": 1})])
            ).status
        )
        self.assertTrue(client.push_users(UserRequest(data=[User(id="u1")])).status)
        self.assertTrue(
            client.push_events(EventRequest(data=[Event(user_id="u1")])).status
        )
        self.assertEqual(
            client.recommend(RecommendRequest(scene="s")).data.results[0].rank_score,
            0.8,
        )
        self.assertEqual(
            client.recommend_items(
                RecommendRequest(debug=True)
            ).data.detail_infos[0].pub_time,
            "123",
        )
        self.assertEqual(
            client.recommend_users(
                RecommendRequest()
            ).data.detail_infos[0].device_id,
            "d2",
        )

        paths = [
            request.full_url.removeprefix("http://openrec.test")
            for request, _ in opener.requests
        ]
        self.assertEqual(
            paths,
            [
                "/api/push/item",
                "/api/push/user",
                "/api/push/event",
                "/api/recommend",
                "/api/recommend/item",
                "/api/recommend/user",
            ],
        )
        payload = json.loads(opener.requests[0][0].data)
        self.assertTrue(payload["requestId"])
        self.assertEqual(payload["body"]["cmd"], "INSERT")
        self.assertEqual(payload["body"]["data"][0]["id"], "i1")
        self.assertEqual(payload["body"]["data"][0]["pubTime"], "123")
        self.assertEqual(payload["body"]["data"][0]["extFields"], {"x": 1})
        self.assertEqual(opener.requests[0][1], 2)

    def test_explicit_envelope_and_request_id(self):
        opener = Opener()
        client = RecClient("http://openrec.test", opener=opener)
        request = JsonRequest(
            request_id="trace-42",
            body=ItemRequest(cmd=PushCmd.UPDATE, data=[Item(id="i1")]),
        )
        client.push_items_request(request)
        payload = json.loads(opener.requests[0][0].data)
        self.assertEqual(payload["requestId"], "trace-42")
        self.assertEqual(payload["body"]["cmd"], "UPDATE")

    def test_non_2xx_returns_none(self):
        class ErrorOpener:
            def open(self, request, timeout=None):
                raise HTTPError(request.full_url, 400, "bad", {}, None)

        response = RecClient(
            "http://openrec.test", opener=ErrorOpener()
        ).push_items(ItemRequest())
        self.assertIsNone(response)

    def test_transport_and_json_errors_are_raised(self):
        class TransportOpener:
            def open(self, request, timeout=None):
                raise URLError("offline")

        with self.assertRaises(URLError):
            RecClient(
                "http://openrec.test", opener=TransportOpener()
            ).push_items(ItemRequest())

        class JSONOpener:
            def open(self, request, timeout=None):
                return Response(b"not-json")

        with self.assertRaises(json.JSONDecodeError):
            RecClient("http://openrec.test", opener=JSONOpener()).push_items(
                ItemRequest()
            )


if __name__ == "__main__":
    unittest.main()
