from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class KLine(_message.Message):
    __slots__ = ("code", "name", "time_key", "open", "close", "high", "low", "volume", "turnover")
    CODE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TIME_KEY_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    LOW_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    TURNOVER_FIELD_NUMBER: _ClassVar[int]
    code: str
    name: str
    time_key: str
    open: float
    close: float
    high: float
    low: float
    volume: int
    turnover: float
    def __init__(self, code: _Optional[str] = ..., name: _Optional[str] = ..., time_key: _Optional[str] = ..., open: _Optional[float] = ..., close: _Optional[float] = ..., high: _Optional[float] = ..., low: _Optional[float] = ..., volume: _Optional[int] = ..., turnover: _Optional[float] = ...) -> None: ...
