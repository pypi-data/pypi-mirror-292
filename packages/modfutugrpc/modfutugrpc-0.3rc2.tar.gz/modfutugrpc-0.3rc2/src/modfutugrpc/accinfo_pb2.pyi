from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AccInfo(_message.Message):
    __slots__ = ("power", "max_power_short", "net_cash_power", "total_assets", "cash", "market_val")
    POWER_FIELD_NUMBER: _ClassVar[int]
    MAX_POWER_SHORT_FIELD_NUMBER: _ClassVar[int]
    NET_CASH_POWER_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ASSETS_FIELD_NUMBER: _ClassVar[int]
    CASH_FIELD_NUMBER: _ClassVar[int]
    MARKET_VAL_FIELD_NUMBER: _ClassVar[int]
    power: float
    max_power_short: float
    net_cash_power: float
    total_assets: float
    cash: float
    market_val: float
    def __init__(self, power: _Optional[float] = ..., max_power_short: _Optional[float] = ..., net_cash_power: _Optional[float] = ..., total_assets: _Optional[float] = ..., cash: _Optional[float] = ..., market_val: _Optional[float] = ...) -> None: ...
