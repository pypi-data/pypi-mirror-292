from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SubscribePublish(_message.Message):
    __slots__ = ("subscribe_to", "publish_to")
    SUBSCRIBE_TO_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_TO_FIELD_NUMBER: _ClassVar[int]
    subscribe_to: str
    publish_to: str
    def __init__(self, subscribe_to: _Optional[str] = ..., publish_to: _Optional[str] = ...) -> None: ...

class BidAskDivergeConf(_message.Message):
    __slots__ = ("subscribePublish",)
    SUBSCRIBEPUBLISH_FIELD_NUMBER: _ClassVar[int]
    subscribePublish: SubscribePublish
    def __init__(self, subscribePublish: _Optional[_Union[SubscribePublish, _Mapping]] = ...) -> None: ...

class MonotonicConf(_message.Message):
    __slots__ = ("count", "increasing", "subscribePublish")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    INCREASING_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIBEPUBLISH_FIELD_NUMBER: _ClassVar[int]
    count: int
    increasing: bool
    subscribePublish: SubscribePublish
    def __init__(self, count: _Optional[int] = ..., increasing: bool = ..., subscribePublish: _Optional[_Union[SubscribePublish, _Mapping]] = ...) -> None: ...
