from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SubscribePublish(_message.Message):
    __slots__ = ("subscribe_to", "publish_to")
    SUBSCRIBE_TO_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_TO_FIELD_NUMBER: _ClassVar[int]
    subscribe_to: str
    publish_to: str
    def __init__(self, subscribe_to: _Optional[str] = ..., publish_to: _Optional[str] = ...) -> None: ...

class CryptoTickerOStreamConf(_message.Message):
    __slots__ = ("subscribePublish",)
    SUBSCRIBEPUBLISH_FIELD_NUMBER: _ClassVar[int]
    subscribePublish: _containers.RepeatedCompositeFieldContainer[SubscribePublish]
    def __init__(self, subscribePublish: _Optional[_Iterable[_Union[SubscribePublish, _Mapping]]] = ...) -> None: ...

class StockQuoteOStreamConf(_message.Message):
    __slots__ = ("subscribePublish",)
    SUBSCRIBEPUBLISH_FIELD_NUMBER: _ClassVar[int]
    subscribePublish: _containers.RepeatedCompositeFieldContainer[SubscribePublish]
    def __init__(self, subscribePublish: _Optional[_Iterable[_Union[SubscribePublish, _Mapping]]] = ...) -> None: ...
