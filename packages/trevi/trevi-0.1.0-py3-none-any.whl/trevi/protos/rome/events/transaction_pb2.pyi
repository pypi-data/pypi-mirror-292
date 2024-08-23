from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Transaction(_message.Message):
    __slots__ = ("source", "to", "amount")
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    source: str
    to: str
    amount: float
    def __init__(self, source: _Optional[str] = ..., to: _Optional[str] = ..., amount: _Optional[float] = ...) -> None: ...
