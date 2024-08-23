from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ThreeTickUp(_message.Message):
    __slots__ = ("subscribe_to",)
    SUBSCRIBE_TO_FIELD_NUMBER: _ClassVar[int]
    subscribe_to: str
    def __init__(self, subscribe_to: _Optional[str] = ...) -> None: ...
