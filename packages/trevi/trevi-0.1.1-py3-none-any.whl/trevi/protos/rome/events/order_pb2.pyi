from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Brokerage(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BACKTEST: _ClassVar[Brokerage]

class OrderSide(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BUY: _ClassVar[OrderSide]
    SELL: _ClassVar[OrderSide]

class OrderType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MARKET: _ClassVar[OrderType]
    LIMIT: _ClassVar[OrderType]

class OrderStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PLACED: _ClassVar[OrderStatus]
    FILLED: _ClassVar[OrderStatus]
BACKTEST: Brokerage
BUY: OrderSide
SELL: OrderSide
MARKET: OrderType
LIMIT: OrderType
PLACED: OrderStatus
FILLED: OrderStatus

class PortfolioDetails(_message.Message):
    __slots__ = ("account_id", "name")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    name: str
    def __init__(self, account_id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class Order(_message.Message):
    __slots__ = ("asset", "order_id", "order_type", "side", "price", "quantity", "timestamp", "strategy", "status", "brokerage", "portfolio")
    ASSET_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    BROKERAGE_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_FIELD_NUMBER: _ClassVar[int]
    asset: str
    order_id: str
    order_type: OrderType
    side: OrderSide
    price: float
    quantity: float
    timestamp: _timestamp_pb2.Timestamp
    strategy: str
    status: OrderStatus
    brokerage: Brokerage
    portfolio: PortfolioDetails
    def __init__(self, asset: _Optional[str] = ..., order_id: _Optional[str] = ..., order_type: _Optional[_Union[OrderType, str]] = ..., side: _Optional[_Union[OrderSide, str]] = ..., price: _Optional[float] = ..., quantity: _Optional[float] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., strategy: _Optional[str] = ..., status: _Optional[_Union[OrderStatus, str]] = ..., brokerage: _Optional[_Union[Brokerage, str]] = ..., portfolio: _Optional[_Union[PortfolioDetails, _Mapping]] = ...) -> None: ...
