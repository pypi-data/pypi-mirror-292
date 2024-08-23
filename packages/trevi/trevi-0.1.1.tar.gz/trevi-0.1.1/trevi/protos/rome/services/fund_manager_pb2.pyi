from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Transaction(_message.Message):
    __slots__ = ()
    class Transfer(_message.Message):
        __slots__ = ("to", "amount")
        FROM_FIELD_NUMBER: _ClassVar[int]
        TO_FIELD_NUMBER: _ClassVar[int]
        AMOUNT_FIELD_NUMBER: _ClassVar[int]
        to: str
        amount: float
        def __init__(self, to: _Optional[str] = ..., amount: _Optional[float] = ..., **kwargs) -> None: ...
    class Trade(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    def __init__(self) -> None: ...

class Portfolio(_message.Message):
    __slots__ = ("id", "name", "account_name")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_NAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    account_name: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., account_name: _Optional[str] = ...) -> None: ...

class Account(_message.Message):
    __slots__ = ("id", "name", "balance")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    balance: float
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., balance: _Optional[float] = ...) -> None: ...

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("ok",)
    OK_FIELD_NUMBER: _ClassVar[int]
    ok: bool
    def __init__(self, ok: bool = ...) -> None: ...

class CreateAccountRequest(_message.Message):
    __slots__ = ("name", "debug")
    class Debug(_message.Message):
        __slots__ = ("include_req_in_resp",)
        INCLUDE_REQ_IN_RESP_FIELD_NUMBER: _ClassVar[int]
        include_req_in_resp: bool
        def __init__(self, include_req_in_resp: bool = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    DEBUG_FIELD_NUMBER: _ClassVar[int]
    name: str
    debug: CreateAccountRequest.Debug
    def __init__(self, name: _Optional[str] = ..., debug: _Optional[_Union[CreateAccountRequest.Debug, _Mapping]] = ...) -> None: ...

class CreateAccountResponse(_message.Message):
    __slots__ = ("account", "request")
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    account: Account
    request: CreateAccountRequest
    def __init__(self, account: _Optional[_Union[Account, _Mapping]] = ..., request: _Optional[_Union[CreateAccountRequest, _Mapping]] = ...) -> None: ...

class DepositFundsToAccountRequest(_message.Message):
    __slots__ = ("account_id", "source", "amount", "debug")
    class Debug(_message.Message):
        __slots__ = ("include_req_in_resp",)
        INCLUDE_REQ_IN_RESP_FIELD_NUMBER: _ClassVar[int]
        include_req_in_resp: bool
        def __init__(self, include_req_in_resp: bool = ...) -> None: ...
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    DEBUG_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    source: str
    amount: float
    debug: DepositFundsToAccountRequest.Debug
    def __init__(self, account_id: _Optional[str] = ..., source: _Optional[str] = ..., amount: _Optional[float] = ..., debug: _Optional[_Union[DepositFundsToAccountRequest.Debug, _Mapping]] = ...) -> None: ...

class DepositFundsToAccountResponse(_message.Message):
    __slots__ = ("account", "request")
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    account: Account
    request: DepositFundsToAccountRequest
    def __init__(self, account: _Optional[_Union[Account, _Mapping]] = ..., request: _Optional[_Union[DepositFundsToAccountRequest, _Mapping]] = ...) -> None: ...

class WithdrawFundsFromAccountRequest(_message.Message):
    __slots__ = ("account_id", "sink", "amount", "debug")
    class Debug(_message.Message):
        __slots__ = ("include_req_in_resp",)
        INCLUDE_REQ_IN_RESP_FIELD_NUMBER: _ClassVar[int]
        include_req_in_resp: bool
        def __init__(self, include_req_in_resp: bool = ...) -> None: ...
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    SINK_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    DEBUG_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    sink: str
    amount: float
    debug: WithdrawFundsFromAccountRequest.Debug
    def __init__(self, account_id: _Optional[str] = ..., sink: _Optional[str] = ..., amount: _Optional[float] = ..., debug: _Optional[_Union[WithdrawFundsFromAccountRequest.Debug, _Mapping]] = ...) -> None: ...

class WithdrawFundsFromAccountResponse(_message.Message):
    __slots__ = ("account", "request")
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    account: Account
    request: WithdrawFundsFromAccountRequest
    def __init__(self, account: _Optional[_Union[Account, _Mapping]] = ..., request: _Optional[_Union[WithdrawFundsFromAccountRequest, _Mapping]] = ...) -> None: ...

class SubscribeFundsToPortfolioRequest(_message.Message):
    __slots__ = ("account_id", "portfolio_id", "amount", "debug")
    class Debug(_message.Message):
        __slots__ = ("include_req_in_resp",)
        INCLUDE_REQ_IN_RESP_FIELD_NUMBER: _ClassVar[int]
        include_req_in_resp: bool
        def __init__(self, include_req_in_resp: bool = ...) -> None: ...
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    DEBUG_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    portfolio_id: str
    amount: float
    debug: SubscribeFundsToPortfolioRequest.Debug
    def __init__(self, account_id: _Optional[str] = ..., portfolio_id: _Optional[str] = ..., amount: _Optional[float] = ..., debug: _Optional[_Union[SubscribeFundsToPortfolioRequest.Debug, _Mapping]] = ...) -> None: ...

class SubscribeFundsToPortfolioResponse(_message.Message):
    __slots__ = ("account_id", "portfolio_id", "balance", "request")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_ID_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    portfolio_id: str
    balance: float
    request: SubscribeFundsToPortfolioRequest
    def __init__(self, account_id: _Optional[str] = ..., portfolio_id: _Optional[str] = ..., balance: _Optional[float] = ..., request: _Optional[_Union[SubscribeFundsToPortfolioRequest, _Mapping]] = ...) -> None: ...

class WithdrawFundsFromPortfolioRequest(_message.Message):
    __slots__ = ("account_id", "portfolio_id", "amount", "debug")
    class Debug(_message.Message):
        __slots__ = ("include_req_in_resp",)
        INCLUDE_REQ_IN_RESP_FIELD_NUMBER: _ClassVar[int]
        include_req_in_resp: bool
        def __init__(self, include_req_in_resp: bool = ...) -> None: ...
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    DEBUG_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    portfolio_id: str
    amount: float
    debug: WithdrawFundsFromPortfolioRequest.Debug
    def __init__(self, account_id: _Optional[str] = ..., portfolio_id: _Optional[str] = ..., amount: _Optional[float] = ..., debug: _Optional[_Union[WithdrawFundsFromPortfolioRequest.Debug, _Mapping]] = ...) -> None: ...

class WithdrawFundsFromPortfolioResponse(_message.Message):
    __slots__ = ("account_id", "portfolio_id", "balance", "request")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    PORTFOLIO_ID_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    account_id: str
    portfolio_id: str
    balance: float
    request: WithdrawFundsFromPortfolioRequest
    def __init__(self, account_id: _Optional[str] = ..., portfolio_id: _Optional[str] = ..., balance: _Optional[float] = ..., request: _Optional[_Union[WithdrawFundsFromPortfolioRequest, _Mapping]] = ...) -> None: ...
