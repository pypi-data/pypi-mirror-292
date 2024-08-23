from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Tick(_message.Message):
    __slots__ = ("timestamp", "product", "bid", "ask")
    class Side(_message.Message):
        __slots__ = ("price", "quantity")
        PRICE_FIELD_NUMBER: _ClassVar[int]
        QUANTITY_FIELD_NUMBER: _ClassVar[int]
        price: float
        quantity: float
        def __init__(self, price: _Optional[float] = ..., quantity: _Optional[float] = ...) -> None: ...
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    BID_FIELD_NUMBER: _ClassVar[int]
    ASK_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    product: str
    bid: Tick.Side
    ask: Tick.Side
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., product: _Optional[str] = ..., bid: _Optional[_Union[Tick.Side, _Mapping]] = ..., ask: _Optional[_Union[Tick.Side, _Mapping]] = ...) -> None: ...
