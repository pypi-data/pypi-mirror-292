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

class TickPubConfiguration(_message.Message):
    __slots__ = ("clock_stream", "subpub")
    CLOCK_STREAM_FIELD_NUMBER: _ClassVar[int]
    SUBPUB_FIELD_NUMBER: _ClassVar[int]
    clock_stream: str
    subpub: _containers.RepeatedCompositeFieldContainer[SubscribePublish]
    def __init__(self, clock_stream: _Optional[str] = ..., subpub: _Optional[_Iterable[_Union[SubscribePublish, _Mapping]]] = ...) -> None: ...
