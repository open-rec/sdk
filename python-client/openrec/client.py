import json
from typing import Any, Dict, List, Optional, Type, TypeVar
from urllib.error import HTTPError
from urllib.request import OpenerDirector, Request, build_opener

from .models import (
    EventRequest,
    Item,
    ItemRequest,
    JsonRequest,
    JsonResponse,
    RecommendRequest,
    RecommendResponse,
    ScoreResult,
    User,
    UserRequest,
)


T = TypeVar("T")


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
    ) -> Optional[JsonResponse[str]]:
        return self.push_items_request(self._envelope(request, request_id))

    def push_users(
        self, request: UserRequest, *, request_id: Optional[str] = None
    ) -> Optional[JsonResponse[str]]:
        return self.push_users_request(self._envelope(request, request_id))

    def push_events(
        self, request: EventRequest, *, request_id: Optional[str] = None
    ) -> Optional[JsonResponse[str]]:
        return self.push_events_request(self._envelope(request, request_id))

    def push_items_request(
        self, request: JsonRequest[ItemRequest]
    ) -> Optional[JsonResponse[str]]:
        return self._post("/api/push/item", request)

    def push_users_request(
        self, request: JsonRequest[UserRequest]
    ) -> Optional[JsonResponse[str]]:
        return self._post("/api/push/user", request)

    def push_events_request(
        self, request: JsonRequest[EventRequest]
    ) -> Optional[JsonResponse[str]]:
        return self._post("/api/push/event", request)

    def recommend(
        self, request: RecommendRequest, *, request_id: Optional[str] = None
    ) -> Optional[JsonResponse[RecommendResponse[Item]]]:
        return self.recommend_request(self._envelope(request, request_id))

    def recommend_items(
        self, request: RecommendRequest, *, request_id: Optional[str] = None
    ) -> Optional[JsonResponse[RecommendResponse[Item]]]:
        return self.recommend_items_request(self._envelope(request, request_id))

    def recommend_users(
        self, request: RecommendRequest, *, request_id: Optional[str] = None
    ) -> Optional[JsonResponse[RecommendResponse[User]]]:
        return self.recommend_users_request(self._envelope(request, request_id))

    def recommend_request(
        self, request: JsonRequest[RecommendRequest]
    ) -> Optional[JsonResponse[RecommendResponse[Item]]]:
        raw = self._post("/api/recommend", request)
        return _recommend_response(raw, Item)

    def recommend_items_request(
        self, request: JsonRequest[RecommendRequest]
    ) -> Optional[JsonResponse[RecommendResponse[Item]]]:
        raw = self._post("/api/recommend/item", request)
        return _recommend_response(raw, Item)

    def recommend_users_request(
        self, request: JsonRequest[RecommendRequest]
    ) -> Optional[JsonResponse[RecommendResponse[User]]]:
        raw = self._post("/api/recommend/user", request)
        return _recommend_response(raw, User)

    def _post(self, path: str, envelope: JsonRequest[Any]) -> Optional[JsonResponse[Any]]:
        payload = json.dumps(envelope.to_dict(), separators=(",", ":")).encode()
        request = Request(
            self.endpoint + path,
            data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        try:
            response = self.opener.open(request, timeout=self.timeout)
        except HTTPError as error:
            error.close()
            return None
        with response:
            raw = json.load(response)
        return JsonResponse(
            code=raw["code"],
            status=raw["status"],
            msg=raw.get("msg", ""),
            data=raw.get("data"),
        )

    @staticmethod
    def _envelope(body: T, request_id: Optional[str]) -> JsonRequest[T]:
        if request_id is None:
            return JsonRequest(body=body)
        return JsonRequest(body=body, request_id=request_id)


def _recommend_response(
    response: Optional[JsonResponse[Dict[str, Any]]], detail_type: Type[T]
) -> Optional[JsonResponse[RecommendResponse[T]]]:
    if response is None or response.data is None:
        return response  # type: ignore[return-value]
    data = response.data
    details: Optional[List[T]] = None
    if data.get("detailInfos") is not None:
        details = [_from_json(detail_type, value) for value in data["detailInfos"]]
    result = RecommendResponse(
        results=[_from_json(ScoreResult, value) for value in data.get("results", [])],
        detail_infos=details,
    )
    return JsonResponse(response.code, response.status, response.msg, result)


_PYTHON_NAMES = {
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


def _from_json(model_type: Type[T], value: Dict[str, Any]) -> T:
    return model_type(**{_PYTHON_NAMES.get(key, key): item for key, item in value.items()})
