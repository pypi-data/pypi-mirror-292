from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ClockConfiguration(_message.Message):
    __slots__ = ("start", "end", "wait_milliseconds", "increment_seconds")
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    WAIT_MILLISECONDS_FIELD_NUMBER: _ClassVar[int]
    INCREMENT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    start: _timestamp_pb2.Timestamp
    end: _timestamp_pb2.Timestamp
    wait_milliseconds: float
    increment_seconds: float
    def __init__(self, start: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., wait_milliseconds: _Optional[float] = ..., increment_seconds: _Optional[float] = ...) -> None: ...
