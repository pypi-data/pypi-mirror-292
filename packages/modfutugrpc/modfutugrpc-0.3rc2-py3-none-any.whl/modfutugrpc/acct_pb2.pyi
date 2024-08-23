from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Acct(_message.Message):
    __slots__ = ("acc_id", "trd_env", "acc_type")
    ACC_ID_FIELD_NUMBER: _ClassVar[int]
    TRD_ENV_FIELD_NUMBER: _ClassVar[int]
    ACC_TYPE_FIELD_NUMBER: _ClassVar[int]
    acc_id: str
    trd_env: str
    acc_type: str
    def __init__(self, acc_id: _Optional[str] = ..., trd_env: _Optional[str] = ..., acc_type: _Optional[str] = ...) -> None: ...
