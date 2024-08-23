from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[Status]
    PENDING: _ClassVar[Status]
    APPROVED: _ClassVar[Status]
    REJECTED: _ClassVar[Status]

class TimeInForce(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IOC: _ClassVar[TimeInForce]
    FOK: _ClassVar[TimeInForce]
    GTC: _ClassVar[TimeInForce]
UNKNOWN: Status
PENDING: Status
APPROVED: Status
REJECTED: Status
IOC: TimeInForce
FOK: TimeInForce
GTC: TimeInForce

class EquityMarketBuy(_message.Message):
    __slots__ = ("ticker", "quantity", "time_in_force")
    TICKER_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    TIME_IN_FORCE_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    quantity: float
    time_in_force: TimeInForce
    def __init__(self, ticker: _Optional[str] = ..., quantity: _Optional[float] = ..., time_in_force: _Optional[_Union[TimeInForce, str]] = ...) -> None: ...

class EquityMarketSell(_message.Message):
    __slots__ = ("ticker", "quantity", "time_in_force")
    TICKER_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    TIME_IN_FORCE_FIELD_NUMBER: _ClassVar[int]
    ticker: str
    quantity: float
    time_in_force: TimeInForce
    def __init__(self, ticker: _Optional[str] = ..., quantity: _Optional[float] = ..., time_in_force: _Optional[_Union[TimeInForce, str]] = ...) -> None: ...

class CryptoMarketBuy(_message.Message):
    __slots__ = ("symbol", "quantity", "time_in_force")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    TIME_IN_FORCE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    quantity: float
    time_in_force: TimeInForce
    def __init__(self, symbol: _Optional[str] = ..., quantity: _Optional[float] = ..., time_in_force: _Optional[_Union[TimeInForce, str]] = ...) -> None: ...

class CryptoMarketSell(_message.Message):
    __slots__ = ("symbol", "quantity", "time_in_force")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    TIME_IN_FORCE_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    quantity: float
    time_in_force: TimeInForce
    def __init__(self, symbol: _Optional[str] = ..., quantity: _Optional[float] = ..., time_in_force: _Optional[_Union[TimeInForce, str]] = ...) -> None: ...

class PortfolioDetails(_message.Message):
    __slots__ = ("account_id", "name")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    name: str
    def __init__(self, account_id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class Trade(_message.Message):
    __slots__ = ("timestamp", "strategy", "portfolio", "equity_market_buy", "equity_market_sell", "crypto_market_buy", "crypto_market_sell")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    STRATEGY_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_FIELD_NUMBER: _ClassVar[int]
    EQUITY_MARKET_BUY_FIELD_NUMBER: _ClassVar[int]
    EQUITY_MARKET_SELL_FIELD_NUMBER: _ClassVar[int]
    CRYPTO_MARKET_BUY_FIELD_NUMBER: _ClassVar[int]
    CRYPTO_MARKET_SELL_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    strategy: str
    portfolio: PortfolioDetails
    equity_market_buy: EquityMarketBuy
    equity_market_sell: EquityMarketSell
    crypto_market_buy: CryptoMarketBuy
    crypto_market_sell: CryptoMarketSell
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., strategy: _Optional[str] = ..., portfolio: _Optional[_Union[PortfolioDetails, _Mapping]] = ..., equity_market_buy: _Optional[_Union[EquityMarketBuy, _Mapping]] = ..., equity_market_sell: _Optional[_Union[EquityMarketSell, _Mapping]] = ..., crypto_market_buy: _Optional[_Union[CryptoMarketBuy, _Mapping]] = ..., crypto_market_sell: _Optional[_Union[CryptoMarketSell, _Mapping]] = ...) -> None: ...

class FilledItem(_message.Message):
    __slots__ = ("symbol", "quantity", "price", "broker", "trade_id")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    BROKER_FIELD_NUMBER: _ClassVar[int]
    TRADE_ID_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    quantity: float
    price: float
    broker: str
    trade_id: str
    def __init__(self, symbol: _Optional[str] = ..., quantity: _Optional[float] = ..., price: _Optional[float] = ..., broker: _Optional[str] = ..., trade_id: _Optional[str] = ...) -> None: ...

class Filled(_message.Message):
    __slots__ = ("items", "trade_id")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    TRADE_ID_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[FilledItem]
    trade_id: str
    def __init__(self, items: _Optional[_Iterable[_Union[FilledItem, _Mapping]]] = ..., trade_id: _Optional[str] = ...) -> None: ...

class PlacedItem(_message.Message):
    __slots__ = ("trade", "trade_id")
    TRADE_FIELD_NUMBER: _ClassVar[int]
    TRADE_ID_FIELD_NUMBER: _ClassVar[int]
    trade: Trade
    trade_id: str
    def __init__(self, trade: _Optional[_Union[Trade, _Mapping]] = ..., trade_id: _Optional[str] = ...) -> None: ...

class Placed(_message.Message):
    __slots__ = ("items", "trade_id")
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    TRADE_ID_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[PlacedItem]
    trade_id: str
    def __init__(self, items: _Optional[_Iterable[_Union[PlacedItem, _Mapping]]] = ..., trade_id: _Optional[str] = ...) -> None: ...

class TradeUpdate(_message.Message):
    __slots__ = ("timestamp", "placed", "filled")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PLACED_FIELD_NUMBER: _ClassVar[int]
    FILLED_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    placed: Placed
    filled: Filled
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., placed: _Optional[_Union[Placed, _Mapping]] = ..., filled: _Optional[_Union[Filled, _Mapping]] = ...) -> None: ...
