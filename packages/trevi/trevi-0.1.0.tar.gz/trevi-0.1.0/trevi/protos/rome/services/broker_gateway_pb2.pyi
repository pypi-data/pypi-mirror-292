from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AssetType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EQUITY: _ClassVar[AssetType]
    CRYPTO: _ClassVar[AssetType]

class OrderSide(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BUY: _ClassVar[OrderSide]
    SELL: _ClassVar[OrderSide]

class TimeInForce(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IOC: _ClassVar[TimeInForce]
    FOK: _ClassVar[TimeInForce]
    GTC: _ClassVar[TimeInForce]

class OrderStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[OrderStatus]
    PENDING: _ClassVar[OrderStatus]
    FILLED: _ClassVar[OrderStatus]
    CANCELLED: _ClassVar[OrderStatus]
    REJECTED: _ClassVar[OrderStatus]
EQUITY: AssetType
CRYPTO: AssetType
BUY: OrderSide
SELL: OrderSide
IOC: TimeInForce
FOK: TimeInForce
GTC: TimeInForce
UNKNOWN: OrderStatus
PENDING: OrderStatus
FILLED: OrderStatus
CANCELLED: OrderStatus
REJECTED: OrderStatus

class ConditionalTrading(_message.Message):
    __slots__ = ("take_profit", "stop_loss")
    class TakeProfit(_message.Message):
        __slots__ = ("limit_price",)
        LIMIT_PRICE_FIELD_NUMBER: _ClassVar[int]
        limit_price: float
        def __init__(self, limit_price: _Optional[float] = ...) -> None: ...
    class StopLoss(_message.Message):
        __slots__ = ("stop_price", "limit_price")
        STOP_PRICE_FIELD_NUMBER: _ClassVar[int]
        LIMIT_PRICE_FIELD_NUMBER: _ClassVar[int]
        stop_price: float
        limit_price: float
        def __init__(self, stop_price: _Optional[float] = ..., limit_price: _Optional[float] = ...) -> None: ...
    TAKE_PROFIT_FIELD_NUMBER: _ClassVar[int]
    STOP_LOSS_FIELD_NUMBER: _ClassVar[int]
    take_profit: ConditionalTrading.TakeProfit
    stop_loss: ConditionalTrading.StopLoss
    def __init__(self, take_profit: _Optional[_Union[ConditionalTrading.TakeProfit, _Mapping]] = ..., stop_loss: _Optional[_Union[ConditionalTrading.StopLoss, _Mapping]] = ...) -> None: ...

class Asset(_message.Message):
    __slots__ = ("type", "symbol")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    type: AssetType
    symbol: str
    def __init__(self, type: _Optional[_Union[AssetType, str]] = ..., symbol: _Optional[str] = ...) -> None: ...

class MarketOrder(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class LimitOrder(_message.Message):
    __slots__ = ("price",)
    PRICE_FIELD_NUMBER: _ClassVar[int]
    price: float
    def __init__(self, price: _Optional[float] = ...) -> None: ...

class PortfolioDetails(_message.Message):
    __slots__ = ("account_id", "name")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    name: str
    def __init__(self, account_id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class Order(_message.Message):
    __slots__ = ("asset", "quantity", "side", "portfolio", "time_in_force", "market", "limit", "conditional_trading")
    ASSET_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_FIELD_NUMBER: _ClassVar[int]
    TIME_IN_FORCE_FIELD_NUMBER: _ClassVar[int]
    MARKET_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    CONDITIONAL_TRADING_FIELD_NUMBER: _ClassVar[int]
    asset: Asset
    quantity: float
    side: OrderSide
    portfolio: PortfolioDetails
    time_in_force: TimeInForce
    market: MarketOrder
    limit: LimitOrder
    conditional_trading: ConditionalTrading
    def __init__(self, asset: _Optional[_Union[Asset, _Mapping]] = ..., quantity: _Optional[float] = ..., side: _Optional[_Union[OrderSide, str]] = ..., portfolio: _Optional[_Union[PortfolioDetails, _Mapping]] = ..., time_in_force: _Optional[_Union[TimeInForce, str]] = ..., market: _Optional[_Union[MarketOrder, _Mapping]] = ..., limit: _Optional[_Union[LimitOrder, _Mapping]] = ..., conditional_trading: _Optional[_Union[ConditionalTrading, _Mapping]] = ...) -> None: ...

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("ok",)
    OK_FIELD_NUMBER: _ClassVar[int]
    ok: bool
    def __init__(self, ok: bool = ...) -> None: ...

class GetTimeRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetTimeResponse(_message.Message):
    __slots__ = ("timestamp",)
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class SubmitOrderRequest(_message.Message):
    __slots__ = ("order",)
    ORDER_FIELD_NUMBER: _ClassVar[int]
    order: Order
    def __init__(self, order: _Optional[_Union[Order, _Mapping]] = ...) -> None: ...

class SubmitOrderResponse(_message.Message):
    __slots__ = ("order", "id")
    ORDER_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    order: Order
    id: str
    def __init__(self, order: _Optional[_Union[Order, _Mapping]] = ..., id: _Optional[str] = ...) -> None: ...

class OrderStatusRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class OrderStatusResponse(_message.Message):
    __slots__ = ("id", "order", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: str
    order: Order
    status: OrderStatus
    def __init__(self, id: _Optional[str] = ..., order: _Optional[_Union[Order, _Mapping]] = ..., status: _Optional[_Union[OrderStatus, str]] = ...) -> None: ...
