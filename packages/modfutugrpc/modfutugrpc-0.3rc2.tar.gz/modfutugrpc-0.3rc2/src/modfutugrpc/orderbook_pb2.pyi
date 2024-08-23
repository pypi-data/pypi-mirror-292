from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OrderBook(_message.Message):
    __slots__ = ("code", "svr_recv_time_bid", "svr_recv_time_ask", "Bid", "Ask")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SVR_RECV_TIME_BID_FIELD_NUMBER: _ClassVar[int]
    SVR_RECV_TIME_ASK_FIELD_NUMBER: _ClassVar[int]
    BID_FIELD_NUMBER: _ClassVar[int]
    ASK_FIELD_NUMBER: _ClassVar[int]
    code: str
    svr_recv_time_bid: str
    svr_recv_time_ask: str
    Bid: _containers.RepeatedCompositeFieldContainer[OBQuo]
    Ask: _containers.RepeatedCompositeFieldContainer[OBQuo]
    def __init__(self, code: _Optional[str] = ..., svr_recv_time_bid: _Optional[str] = ..., svr_recv_time_ask: _Optional[str] = ..., Bid: _Optional[_Iterable[_Union[OBQuo, _Mapping]]] = ..., Ask: _Optional[_Iterable[_Union[OBQuo, _Mapping]]] = ...) -> None: ...

class OBQuo(_message.Message):
    __slots__ = ("price", "volume")
    PRICE_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    price: float
    volume: float
    def __init__(self, price: _Optional[float] = ..., volume: _Optional[float] = ...) -> None: ...
