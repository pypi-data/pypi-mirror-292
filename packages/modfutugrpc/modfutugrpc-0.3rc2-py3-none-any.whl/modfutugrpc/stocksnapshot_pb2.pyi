from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class StockSnapshot(_message.Message):
    __slots__ = ("code", "name", "update_time", "last_price", "open_price", "high_price", "low_price", "prev_close_price", "volume", "turnover")
    CODE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    UPDATE_TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_PRICE_FIELD_NUMBER: _ClassVar[int]
    OPEN_PRICE_FIELD_NUMBER: _ClassVar[int]
    HIGH_PRICE_FIELD_NUMBER: _ClassVar[int]
    LOW_PRICE_FIELD_NUMBER: _ClassVar[int]
    PREV_CLOSE_PRICE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    TURNOVER_FIELD_NUMBER: _ClassVar[int]
    code: str
    name: str
    update_time: str
    last_price: float
    open_price: float
    high_price: float
    low_price: float
    prev_close_price: float
    volume: float
    turnover: float
    def __init__(self, code: _Optional[str] = ..., name: _Optional[str] = ..., update_time: _Optional[str] = ..., last_price: _Optional[float] = ..., open_price: _Optional[float] = ..., high_price: _Optional[float] = ..., low_price: _Optional[float] = ..., prev_close_price: _Optional[float] = ..., volume: _Optional[float] = ..., turnover: _Optional[float] = ...) -> None: ...
