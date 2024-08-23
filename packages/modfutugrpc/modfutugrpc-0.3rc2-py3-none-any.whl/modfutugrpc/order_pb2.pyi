from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Order(_message.Message):
    __slots__ = ("trd_side", "order_type", "order_status", "order_id", "code", "qty", "price", "create_time", "updated_time", "dealt_qty", "dealt_avg_price", "last_err_msg", "remark")
    TRD_SIDE_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    ORDER_STATUS_FIELD_NUMBER: _ClassVar[int]
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    QTY_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    UPDATED_TIME_FIELD_NUMBER: _ClassVar[int]
    DEALT_QTY_FIELD_NUMBER: _ClassVar[int]
    DEALT_AVG_PRICE_FIELD_NUMBER: _ClassVar[int]
    LAST_ERR_MSG_FIELD_NUMBER: _ClassVar[int]
    REMARK_FIELD_NUMBER: _ClassVar[int]
    trd_side: str
    order_type: str
    order_status: str
    order_id: str
    code: str
    qty: float
    price: float
    create_time: str
    updated_time: str
    dealt_qty: float
    dealt_avg_price: float
    last_err_msg: str
    remark: str
    def __init__(self, trd_side: _Optional[str] = ..., order_type: _Optional[str] = ..., order_status: _Optional[str] = ..., order_id: _Optional[str] = ..., code: _Optional[str] = ..., qty: _Optional[float] = ..., price: _Optional[float] = ..., create_time: _Optional[str] = ..., updated_time: _Optional[str] = ..., dealt_qty: _Optional[float] = ..., dealt_avg_price: _Optional[float] = ..., last_err_msg: _Optional[str] = ..., remark: _Optional[str] = ...) -> None: ...
