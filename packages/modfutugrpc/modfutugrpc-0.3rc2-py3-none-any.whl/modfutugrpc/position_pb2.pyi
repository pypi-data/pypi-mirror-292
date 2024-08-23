from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Position(_message.Message):
    __slots__ = ("code", "qty", "can_sell_qty", "cost_price")
    CODE_FIELD_NUMBER: _ClassVar[int]
    QTY_FIELD_NUMBER: _ClassVar[int]
    CAN_SELL_QTY_FIELD_NUMBER: _ClassVar[int]
    COST_PRICE_FIELD_NUMBER: _ClassVar[int]
    code: str
    qty: float
    can_sell_qty: float
    cost_price: float
    def __init__(self, code: _Optional[str] = ..., qty: _Optional[float] = ..., can_sell_qty: _Optional[float] = ..., cost_price: _Optional[float] = ...) -> None: ...
