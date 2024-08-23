from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SeqQuote(_message.Message):
    __slots__ = ("code", "name", "time", "is_blank", "opened_mins", "cur_price", "volume", "turnover")
    CODE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    IS_BLANK_FIELD_NUMBER: _ClassVar[int]
    OPENED_MINS_FIELD_NUMBER: _ClassVar[int]
    CUR_PRICE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    TURNOVER_FIELD_NUMBER: _ClassVar[int]
    code: str
    name: str
    time: str
    is_blank: bool
    opened_mins: int
    cur_price: float
    volume: float
    turnover: float
    def __init__(self, code: _Optional[str] = ..., name: _Optional[str] = ..., time: _Optional[str] = ..., is_blank: bool = ..., opened_mins: _Optional[int] = ..., cur_price: _Optional[float] = ..., volume: _Optional[float] = ..., turnover: _Optional[float] = ...) -> None: ...
