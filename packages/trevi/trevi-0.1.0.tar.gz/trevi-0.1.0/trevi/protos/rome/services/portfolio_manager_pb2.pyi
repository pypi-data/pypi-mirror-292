from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AssetState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AVAILABLE: _ClassVar[AssetState]
    HOLD: _ClassVar[AssetState]
AVAILABLE: AssetState
HOLD: AssetState

class StateInfo(_message.Message):
    __slots__ = ("state", "assets")
    STATE_FIELD_NUMBER: _ClassVar[int]
    ASSETS_FIELD_NUMBER: _ClassVar[int]
    state: AssetState
    assets: _containers.RepeatedCompositeFieldContainer[PortfolioAsset]
    def __init__(self, state: _Optional[_Union[AssetState, str]] = ..., assets: _Optional[_Iterable[_Union[PortfolioAsset, _Mapping]]] = ...) -> None: ...

class Portfolio(_message.Message):
    __slots__ = ("account_id", "name", "states")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATES_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    name: str
    states: _containers.RepeatedCompositeFieldContainer[StateInfo]
    def __init__(self, account_id: _Optional[str] = ..., name: _Optional[str] = ..., states: _Optional[_Iterable[_Union[StateInfo, _Mapping]]] = ...) -> None: ...

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("ok",)
    OK_FIELD_NUMBER: _ClassVar[int]
    ok: bool
    def __init__(self, ok: bool = ...) -> None: ...

class PortfolioAsset(_message.Message):
    __slots__ = ("name", "amount")
    NAME_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    name: str
    amount: float
    def __init__(self, name: _Optional[str] = ..., amount: _Optional[float] = ...) -> None: ...

class GetAssetRequest(_message.Message):
    __slots__ = ("account_id", "portfolio_name", "asset_name", "state")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_NAME_FIELD_NUMBER: _ClassVar[int]
    ASSET_NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    portfolio_name: str
    asset_name: str
    state: AssetState
    def __init__(self, account_id: _Optional[str] = ..., portfolio_name: _Optional[str] = ..., asset_name: _Optional[str] = ..., state: _Optional[_Union[AssetState, str]] = ...) -> None: ...

class GetAssetResponse(_message.Message):
    __slots__ = ("asset", "request")
    ASSET_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    asset: PortfolioAsset
    request: GetAssetRequest
    def __init__(self, asset: _Optional[_Union[PortfolioAsset, _Mapping]] = ..., request: _Optional[_Union[GetAssetRequest, _Mapping]] = ...) -> None: ...

class CreatePortfolioRequest(_message.Message):
    __slots__ = ("account_id", "name")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    name: str
    def __init__(self, account_id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class CreatePortfolioResponse(_message.Message):
    __slots__ = ("portfolio", "request")
    PORTFOLIO_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    portfolio: Portfolio
    request: CreatePortfolioRequest
    def __init__(self, portfolio: _Optional[_Union[Portfolio, _Mapping]] = ..., request: _Optional[_Union[CreatePortfolioRequest, _Mapping]] = ...) -> None: ...

class TransactRequest(_message.Message):
    __slots__ = ("account_id", "portfolio_name", "buy_side", "sell_side", "sell_from_state")
    class TransactionSide(_message.Message):
        __slots__ = ("asset_name", "amount")
        ASSET_NAME_FIELD_NUMBER: _ClassVar[int]
        AMOUNT_FIELD_NUMBER: _ClassVar[int]
        asset_name: str
        amount: float
        def __init__(self, asset_name: _Optional[str] = ..., amount: _Optional[float] = ...) -> None: ...
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_NAME_FIELD_NUMBER: _ClassVar[int]
    BUY_SIDE_FIELD_NUMBER: _ClassVar[int]
    SELL_SIDE_FIELD_NUMBER: _ClassVar[int]
    SELL_FROM_STATE_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    portfolio_name: str
    buy_side: TransactRequest.TransactionSide
    sell_side: TransactRequest.TransactionSide
    sell_from_state: AssetState
    def __init__(self, account_id: _Optional[str] = ..., portfolio_name: _Optional[str] = ..., buy_side: _Optional[_Union[TransactRequest.TransactionSide, _Mapping]] = ..., sell_side: _Optional[_Union[TransactRequest.TransactionSide, _Mapping]] = ..., sell_from_state: _Optional[_Union[AssetState, str]] = ...) -> None: ...

class TransactResponse(_message.Message):
    __slots__ = ("from_state", "to_state", "request")
    FROM_STATE_FIELD_NUMBER: _ClassVar[int]
    TO_STATE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    from_state: StateInfo
    to_state: StateInfo
    request: TransactRequest
    def __init__(self, from_state: _Optional[_Union[StateInfo, _Mapping]] = ..., to_state: _Optional[_Union[StateInfo, _Mapping]] = ..., request: _Optional[_Union[TransactRequest, _Mapping]] = ...) -> None: ...

class PlaceHoldRequest(_message.Message):
    __slots__ = ("account_id", "portfolio_name", "asset_name", "amount")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_NAME_FIELD_NUMBER: _ClassVar[int]
    ASSET_NAME_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    portfolio_name: str
    asset_name: str
    amount: float
    def __init__(self, account_id: _Optional[str] = ..., portfolio_name: _Optional[str] = ..., asset_name: _Optional[str] = ..., amount: _Optional[float] = ...) -> None: ...

class PlaceHoldResponse(_message.Message):
    __slots__ = ("from_state", "to_state", "request")
    FROM_STATE_FIELD_NUMBER: _ClassVar[int]
    TO_STATE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    from_state: StateInfo
    to_state: StateInfo
    request: PlaceHoldRequest
    def __init__(self, from_state: _Optional[_Union[StateInfo, _Mapping]] = ..., to_state: _Optional[_Union[StateInfo, _Mapping]] = ..., request: _Optional[_Union[PlaceHoldRequest, _Mapping]] = ...) -> None: ...

class ReleaseHoldRequest(_message.Message):
    __slots__ = ("account_id", "portfolio_name", "asset_name", "amount")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_NAME_FIELD_NUMBER: _ClassVar[int]
    ASSET_NAME_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    portfolio_name: str
    asset_name: str
    amount: float
    def __init__(self, account_id: _Optional[str] = ..., portfolio_name: _Optional[str] = ..., asset_name: _Optional[str] = ..., amount: _Optional[float] = ...) -> None: ...

class ReleaseHoldResponse(_message.Message):
    __slots__ = ("from_state", "to_state", "request")
    FROM_STATE_FIELD_NUMBER: _ClassVar[int]
    TO_STATE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    from_state: StateInfo
    to_state: StateInfo
    request: ReleaseHoldRequest
    def __init__(self, from_state: _Optional[_Union[StateInfo, _Mapping]] = ..., to_state: _Optional[_Union[StateInfo, _Mapping]] = ..., request: _Optional[_Union[ReleaseHoldRequest, _Mapping]] = ...) -> None: ...

class GetPortfolioRequest(_message.Message):
    __slots__ = ("account_id", "portfolio_name", "debug")
    class Debug(_message.Message):
        __slots__ = ("include_req_in_resp",)
        INCLUDE_REQ_IN_RESP_FIELD_NUMBER: _ClassVar[int]
        include_req_in_resp: bool
        def __init__(self, include_req_in_resp: bool = ...) -> None: ...
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_NAME_FIELD_NUMBER: _ClassVar[int]
    DEBUG_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    portfolio_name: str
    debug: GetPortfolioRequest.Debug
    def __init__(self, account_id: _Optional[str] = ..., portfolio_name: _Optional[str] = ..., debug: _Optional[_Union[GetPortfolioRequest.Debug, _Mapping]] = ...) -> None: ...

class GetPortfolioResponse(_message.Message):
    __slots__ = ("portfolio", "request")
    PORTFOLIO_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    portfolio: Portfolio
    request: GetPortfolioRequest
    def __init__(self, portfolio: _Optional[_Union[Portfolio, _Mapping]] = ..., request: _Optional[_Union[GetPortfolioRequest, _Mapping]] = ...) -> None: ...

class DepositAssetRequest(_message.Message):
    __slots__ = ("account_id", "portfolio_name", "asset_name", "amount")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_NAME_FIELD_NUMBER: _ClassVar[int]
    ASSET_NAME_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    portfolio_name: str
    asset_name: str
    amount: float
    def __init__(self, account_id: _Optional[str] = ..., portfolio_name: _Optional[str] = ..., asset_name: _Optional[str] = ..., amount: _Optional[float] = ...) -> None: ...

class DepositAssetResponse(_message.Message):
    __slots__ = ("account_id", "portfolio_name", "asset_name", "balance")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_NAME_FIELD_NUMBER: _ClassVar[int]
    ASSET_NAME_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    portfolio_name: str
    asset_name: str
    balance: float
    def __init__(self, account_id: _Optional[str] = ..., portfolio_name: _Optional[str] = ..., asset_name: _Optional[str] = ..., balance: _Optional[float] = ...) -> None: ...

class WithdrawAssetRequest(_message.Message):
    __slots__ = ("account_id", "portfolio_name", "asset_name", "amount")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_NAME_FIELD_NUMBER: _ClassVar[int]
    ASSET_NAME_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    portfolio_name: str
    asset_name: str
    amount: float
    def __init__(self, account_id: _Optional[str] = ..., portfolio_name: _Optional[str] = ..., asset_name: _Optional[str] = ..., amount: _Optional[float] = ...) -> None: ...

class WithdrawAssetResponse(_message.Message):
    __slots__ = ("account_id", "portfolio_name", "asset_name", "balance")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_NAME_FIELD_NUMBER: _ClassVar[int]
    ASSET_NAME_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    portfolio_name: str
    asset_name: str
    balance: float
    def __init__(self, account_id: _Optional[str] = ..., portfolio_name: _Optional[str] = ..., asset_name: _Optional[str] = ..., balance: _Optional[float] = ...) -> None: ...
