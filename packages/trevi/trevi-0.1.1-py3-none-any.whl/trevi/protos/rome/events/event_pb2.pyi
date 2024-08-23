from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Event(_message.Message):
    __slots__ = ("timestamp", "type", "event", "msg")
    class Message(_message.Message):
        __slots__ = ("name", "content", "descriptor_set")
        NAME_FIELD_NUMBER: _ClassVar[int]
        CONTENT_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTOR_SET_FIELD_NUMBER: _ClassVar[int]
        name: str
        content: bytes
        descriptor_set: _descriptor_pb2.FileDescriptorSet
        def __init__(self, name: _Optional[str] = ..., content: _Optional[bytes] = ..., descriptor_set: _Optional[_Union[_descriptor_pb2.FileDescriptorSet, _Mapping]] = ...) -> None: ...
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    type: str
    event: str
    msg: Event.Message
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., type: _Optional[str] = ..., event: _Optional[str] = ..., msg: _Optional[_Union[Event.Message, _Mapping]] = ...) -> None: ...

class Events(_message.Message):
    __slots__ = ("events",)
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    events: _containers.RepeatedCompositeFieldContainer[Event]
    def __init__(self, events: _Optional[_Iterable[_Union[Event, _Mapping]]] = ...) -> None: ...
