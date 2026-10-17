import json
from dataclasses import fields
from typing import Any, Optional, TypeVar
from urllib.error import HTTPError
from urllib.request import OpenerDirector, Request, build_opener

from .models import (
    EventRequest,
    Item,
    ItemRequest,
    JsonRequest,
    JsonResponse,
    RecallDiagnostic,
    RecommendRequest,
    RecommendResponse,
    ScoreResult,
    User,
    UserRequest,
)

T = TypeVar("T")


class RecClientHttpException(RuntimeError):
    """Non-2xx HTTP response, with at most 1024 bytes of response detail."""

    def __init__(self, status_code: int, response_body: str) -> None:
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(f"OpenRec HTTP {status_code}: {response_body}")


class RecClient:
    def __init__(
        self,
        endpoint: str,
        opener: Optional[OpenerDirector] = None,
        timeout: Optional[float] = None,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.opener = opener or build_opener()
        self.timeout = timeout

    def push_items(
        self, request: ItemRequest, *, request_id: Optional[str] = None
    ) -> JsonResponse[str]:
        return self.push_items_request(self._envelope(request, request_id))

    def push_users(
        self, request: UserRequest, *, request_id: Optional[str] = None
    ) -> JsonResponse[str]:
        return self.push_users_request(self._envelope(request, request_id))

    def push_events(
        self, request: EventRequest, *, request_id: Optional[str] = None
    ) -> JsonResponse[str]:
        return self.push_events_request(self._envelope(request, request_id))

    def push_items_request(
        self, request: JsonRequest[ItemRequest]
    ) -> JsonResponse[str]:
        return self._post("/api/push/item", request)

    def push_users_request(
        self, request: JsonRequest[UserRequest]
    ) -> JsonResponse[str]:
        return self._post("/api/push/user", request)

    def push_events_request(
        self, request: JsonRequest[EventRequest]
    ) -> JsonResponse[str]:
        return self._post("/api/push/event", request)

    def recommend(
        self, request: RecommendRequest, *, request_id: Optional[str] = None
    ) -> JsonResponse[RecommendResponse[Item]]:
        return self.recommend_request(self._envelope(request, request_id))

    def recommend_items(
        self, request: RecommendRequest, *, request_id: Optional[str] = None
    ) -> JsonResponse[RecommendResponse[Item]]:
        return self.recommend_items_request(
            self._envelope(request, request_id)
        )

    def recommend_users(
        self, request: RecommendRequest, *, request_id: Optional[str] = None
    ) -> JsonResponse[RecommendResponse[User]]:
        return self.recommend_users_request(
            self._envelope(request, request_id)
        )

    def recommend_request(
        self, request: JsonRequest[RecommendRequest]
    ) -> JsonResponse[RecommendResponse[Item]]:
        raw = self._post("/api/recommend", request)
        return _recommend_response(raw, Item)

    def recommend_items_request(
        self, request: JsonRequest[RecommendRequest]
    ) -> JsonResponse[RecommendResponse[Item]]:
        raw = self._post("/api/recommend/item", request)
        return _recommend_response(raw, Item)

    def recommend_users_request(
        self, request: JsonRequest[RecommendRequest]
    ) -> JsonResponse[RecommendResponse[User]]:
        raw = self._post("/api/recommend/user", request)
        return _recommend_response(raw, User)

    def _post(
        self, path: str, envelope: JsonRequest[Any]
    ) -> JsonResponse[Any]:
        payload = json.dumps(
            envelope.to_dict(), separators=(",", ":")
        ).encode()
        request = Request(
            self.endpoint + path,
            data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        try:
            response = self.opener.open(request, timeout=self.timeout)
        except HTTPError as error:
            try:
                detail = error.read(1024).decode("utf-8", errors="replace")
            finally:
                error.close()
            raise RecClientHttpException(error.code, detail) from error
        with response:
            status = (
                response.getcode() if hasattr(response, "getcode") else 200
            )
            if not 200 <= status < 300:
                detail = response.read(1024).decode("utf-8", errors="replace")
                raise RecClientHttpException(status, detail)
            raw = json.load(response)
        if not isinstance(raw, dict):
            raise ValueError("OpenRec returned a non-object response")
        return JsonResponse(
            code=raw.get("code", 0),
            status=raw.get("status", False),
            msg=raw.get("msg", ""),
            data=raw.get("data"),
        )

    @staticmethod
    def _envelope(body: T, request_id: Optional[str]) -> JsonRequest[T]:
        if request_id is None:
            return JsonRequest(body=body)
        return JsonRequest(body=body, request_id=request_id)


def _recommend_response(
    response: JsonResponse[dict[str, Any]], detail_type: type[T]
) -> JsonResponse[RecommendResponse[T]]:
    if response.data is None:
        return JsonResponse(response.code, response.status, response.msg, None)
    data = response.data
    details: Optional[list[T]] = None
    if data.get("detailInfos") is not None:
        details = [
            _from_json(detail_type, value) for value in data["detailInfos"]
        ]
    result = RecommendResponse(
        results=[
            _from_json(ScoreResult, value)
            for value in (data.get("results") or [])
        ],
        detail_infos=details,
        recall_diagnostics=(
            [
                _from_json(RecallDiagnostic, value)
                for value in data["recallDiagnostics"]
            ]
            if data.get("recallDiagnostics") is not None
            else None
        ),
    )
    return JsonResponse(response.code, response.status, response.msg, result)


_PYTHON_NAMES = {
    "candidateCount": "candidate_count",
    "deviceId": "device_id",
    "userId": "user_id",
    "itemId": "item_id",
    "traceId": "trace_id",
    "isLogin": "is_login",
    "extFields": "ext_fields",
    "pubTime": "pub_time",
    "modifyTime": "modify_time",
    "expireTime": "expire_time",
    "registerTime": "register_time",
    "loginTime": "login_time",
    "recallFrom": "recall_from",
    "recallScore": "recall_score",
    "recallFusionScore": "recall_fusion_score",
    "rankScore": "rank_score",
    "recallScores": "recall_scores",
}


def _from_json(model_type: type[T], value: dict[str, Any]) -> T:
    known = {field.name for field in fields(model_type)}
    values = {
        _PYTHON_NAMES.get(key, key): item
        for key, item in value.items()
        if _PYTHON_NAMES.get(key, key) in known
    }
    return model_type(**values)
