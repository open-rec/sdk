from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
from typing import Any, Generic, Optional, TypeVar
from uuid import uuid4

CODE_SUCCESS = 200
CODE_BAD_REQUEST = 400
CODE_NOT_FOUND = 404
CODE_ERROR = 500
CODE_NOT_IMPLEMENTED = 501
CODE_TIMEOUT = 504

TARGET_ITEM = "item"
TARGET_USER = "user"

T = TypeVar("T")


class PushCmd(str, Enum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


@dataclass
class JsonRequest(Generic[T]):
    body: T
    request_id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> dict[str, Any]:
        return {"requestId": self.request_id, "body": to_json_dict(self.body)}


@dataclass
class JsonResponse(Generic[T]):
    code: int
    status: bool
    msg: str
    data: Optional[T]


@dataclass
class Item:
    id: Optional[str] = None
    weight: int = 0
    title: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    scene: Optional[str] = None
    pub_time: Optional[str] = None
    modify_time: Optional[str] = None
    expire_time: Optional[str] = None
    status: int = 0
    ext_fields: Any = None


@dataclass
class User:
    id: Optional[str] = None
    device_id: Optional[str] = None
    name: Optional[str] = None
    gender: Optional[str] = None
    age: int = 0
    country: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    tags: Optional[list[str]] = None
    register_time: Optional[str] = None
    login_time: Optional[str] = None
    ext_fields: Any = None


@dataclass
class Event:
    user_id: Optional[str] = None
    device_id: Optional[str] = None
    item_id: Optional[str] = None
    trace_id: Optional[str] = None
    scene: Optional[str] = None
    type: Optional[str] = None
    value: Optional[str] = None
    time: Optional[str] = None
    is_login: bool = False
    ext_fields: Any = None


@dataclass
class ItemRequest:
    data: Optional[list[Item]] = None
    cmd: PushCmd = PushCmd.INSERT


@dataclass
class UserRequest:
    data: Optional[list[User]] = None
    cmd: PushCmd = PushCmd.INSERT


@dataclass
class EventRequest:
    data: Optional[list[Event]] = None
    cmd: PushCmd = PushCmd.INSERT


@dataclass
class RecommendRequest:
    scene: Optional[str] = None
    size: int = 0
    user_id: Optional[str] = None
    device_id: Optional[str] = None
    item_ids: Optional[list[str]] = None
    type: Optional[str] = None
    debug: bool = False
    target_type: str = TARGET_ITEM
    params: Optional[dict[str, Any]] = None


@dataclass
class ScoreResult:
    id: Optional[str] = None
    score: float = 0.0
    recall_from: Optional[str] = None
    recall_score: Optional[float] = None
    recall_fusion_score: Optional[float] = None
    rank_score: Optional[float] = None
    recall_scores: Optional[dict[str, float]] = None


@dataclass
class RecommendResponse(Generic[T]):
    results: list[ScoreResult] = field(default_factory=list)
    detail_infos: Optional[list[T]] = None


@dataclass
class DislikeValue:
    id: Optional[str] = None
    category: Optional[str] = None
    tags: list[str] = field(default_factory=list)


@dataclass
class VectorResult:
    id: Optional[str] = None
    vector: Optional[list[float]] = None


_JSON_NAMES = {
    "request_id": "requestId",
    "user_id": "userId",
    "device_id": "deviceId",
    "item_id": "itemId",
    "item_ids": "itemIds",
    "trace_id": "traceId",
    "is_login": "isLogin",
    "ext_fields": "extFields",
    "pub_time": "pubTime",
    "modify_time": "modifyTime",
    "expire_time": "expireTime",
    "register_time": "registerTime",
    "login_time": "loginTime",
    "target_type": "targetType",
    "detail_infos": "detailInfos",
    "recall_from": "recallFrom",
    "recall_score": "recallScore",
    "recall_fusion_score": "recallFusionScore",
    "rank_score": "rankScore",
    "recall_scores": "recallScores",
}


def to_json_dict(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {
            _JSON_NAMES.get(model_field.name, model_field.name): to_json_dict(item)
            for model_field in fields(value)
            for item in [getattr(value, model_field.name)]
            if item is not None
        }
    if isinstance(value, list):
        return [to_json_dict(item) for item in value]
    if isinstance(value, dict):
        return {key: to_json_dict(item) for key, item in value.items()}
    return value
