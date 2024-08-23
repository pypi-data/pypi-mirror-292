from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class OrderFee(_message.Message):
    __slots__ = ("order_id", "fee_amount")
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    FEE_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    fee_amount: float
    def __init__(self, order_id: _Optional[str] = ..., fee_amount: _Optional[float] = ...) -> None: ...
