from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Deal(_message.Message):
    __slots__ = ("trd_side", "deal_id", "order_id", "code", "qty", "price", "create_time", "status")
    TRD_SIDE_FIELD_NUMBER: _ClassVar[int]
    DEAL_ID_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    QTY_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    trd_side: str
    deal_id: str
    order_id: str
    code: str
    qty: float
    price: float
    create_time: str
    status: str
    def __init__(self, trd_side: _Optional[str] = ..., deal_id: _Optional[str] = ..., order_id: _Optional[str] = ..., code: _Optional[str] = ..., qty: _Optional[float] = ..., price: _Optional[float] = ..., create_time: _Optional[str] = ..., status: _Optional[str] = ...) -> None: ...
