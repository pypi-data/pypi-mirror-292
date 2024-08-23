import modfutugrpc.order_pb2 as _order_pb2
import modfutugrpc.position_pb2 as _position_pb2
import modfutugrpc.deal_pb2 as _deal_pb2
import modfutugrpc.orderfee_pb2 as _orderfee_pb2
import modfutugrpc.orderbook_pb2 as _orderbook_pb2
import modfutugrpc.seqquote_pb2 as _seqquote_pb2
import modfutugrpc.stocksnapshot_pb2 as _stocksnapshot_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PlaceOrder_Req(_message.Message):
    __slots__ = ("acc_id", "code", "side", "order_type", "qty", "price")
    ACC_ID_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    QTY_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    acc_id: str
    code: str
    side: str
    order_type: str
    qty: int
    price: float
    def __init__(self, acc_id: _Optional[str] = ..., code: _Optional[str] = ..., side: _Optional[str] = ..., order_type: _Optional[str] = ..., qty: _Optional[int] = ..., price: _Optional[float] = ...) -> None: ...

class PlaceOrder_Res(_message.Message):
    __slots__ = ("trading_order",)
    TRADING_ORDER_FIELD_NUMBER: _ClassVar[int]
    trading_order: _order_pb2.Order
    def __init__(self, trading_order: _Optional[_Union[_order_pb2.Order, _Mapping]] = ...) -> None: ...

class Init_Req(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Init_Res(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetActiveOrders_Req(_message.Message):
    __slots__ = ("acc_id",)
    ACC_ID_FIELD_NUMBER: _ClassVar[int]
    acc_id: str
    def __init__(self, acc_id: _Optional[str] = ...) -> None: ...

class GetActiveOrders_Res(_message.Message):
    __slots__ = ("active_orders",)
    ACTIVE_ORDERS_FIELD_NUMBER: _ClassVar[int]
    active_orders: _containers.RepeatedCompositeFieldContainer[_order_pb2.Order]
    def __init__(self, active_orders: _Optional[_Iterable[_Union[_order_pb2.Order, _Mapping]]] = ...) -> None: ...

class GetHoldings_Req(_message.Message):
    __slots__ = ("acc_id",)
    ACC_ID_FIELD_NUMBER: _ClassVar[int]
    acc_id: str
    def __init__(self, acc_id: _Optional[str] = ...) -> None: ...

class GetHoldings_Res(_message.Message):
    __slots__ = ("holdings",)
    HOLDINGS_FIELD_NUMBER: _ClassVar[int]
    holdings: _containers.RepeatedCompositeFieldContainer[_position_pb2.Position]
    def __init__(self, holdings: _Optional[_Iterable[_Union[_position_pb2.Position, _Mapping]]] = ...) -> None: ...

class FetchRTSeqQuotes_Req(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FetchRTSeqQuotes_Res(_message.Message):
    __slots__ = ("code", "seq_quotes")
    CODE_FIELD_NUMBER: _ClassVar[int]
    SEQ_QUOTES_FIELD_NUMBER: _ClassVar[int]
    code: str
    seq_quotes: _containers.RepeatedCompositeFieldContainer[_seqquote_pb2.SeqQuote]
    def __init__(self, code: _Optional[str] = ..., seq_quotes: _Optional[_Iterable[_Union[_seqquote_pb2.SeqQuote, _Mapping]]] = ...) -> None: ...

class FetchDealOrders_Req(_message.Message):
    __slots__ = ("acc_id",)
    ACC_ID_FIELD_NUMBER: _ClassVar[int]
    acc_id: str
    def __init__(self, acc_id: _Optional[str] = ...) -> None: ...

class FetchDealOrders_Res(_message.Message):
    __slots__ = ("code", "deal_orders")
    CODE_FIELD_NUMBER: _ClassVar[int]
    DEAL_ORDERS_FIELD_NUMBER: _ClassVar[int]
    code: str
    deal_orders: _containers.RepeatedCompositeFieldContainer[_order_pb2.Order]
    def __init__(self, code: _Optional[str] = ..., deal_orders: _Optional[_Iterable[_Union[_order_pb2.Order, _Mapping]]] = ...) -> None: ...

class FetchDealOrderFees_Req(_message.Message):
    __slots__ = ("acc_id",)
    ACC_ID_FIELD_NUMBER: _ClassVar[int]
    acc_id: str
    def __init__(self, acc_id: _Optional[str] = ...) -> None: ...

class FetchDealOrderFees_Res(_message.Message):
    __slots__ = ("code", "order_fees")
    CODE_FIELD_NUMBER: _ClassVar[int]
    ORDER_FEES_FIELD_NUMBER: _ClassVar[int]
    code: str
    order_fees: _containers.RepeatedCompositeFieldContainer[_orderfee_pb2.OrderFee]
    def __init__(self, code: _Optional[str] = ..., order_fees: _Optional[_Iterable[_Union[_orderfee_pb2.OrderFee, _Mapping]]] = ...) -> None: ...

class GetBaseData_Req(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetBaseData_Res(_message.Message):
    __slots__ = ("mkt_session", "snapshot_data")
    MKT_SESSION_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_DATA_FIELD_NUMBER: _ClassVar[int]
    mkt_session: str
    snapshot_data: _containers.RepeatedCompositeFieldContainer[SnapshotData]
    def __init__(self, mkt_session: _Optional[str] = ..., snapshot_data: _Optional[_Iterable[_Union[SnapshotData, _Mapping]]] = ...) -> None: ...

class SnapshotData(_message.Message):
    __slots__ = ("code", "prev_close")
    CODE_FIELD_NUMBER: _ClassVar[int]
    PREV_CLOSE_FIELD_NUMBER: _ClassVar[int]
    code: str
    prev_close: float
    def __init__(self, code: _Optional[str] = ..., prev_close: _Optional[float] = ...) -> None: ...

class OnPushOrderBook_Msg(_message.Message):
    __slots__ = ("orderbook",)
    ORDERBOOK_FIELD_NUMBER: _ClassVar[int]
    orderbook: _orderbook_pb2.OrderBook
    def __init__(self, orderbook: _Optional[_Union[_orderbook_pb2.OrderBook, _Mapping]] = ...) -> None: ...

class OnPushSeqQuote_Msg(_message.Message):
    __slots__ = ("seq_quote",)
    SEQ_QUOTE_FIELD_NUMBER: _ClassVar[int]
    seq_quote: _seqquote_pb2.SeqQuote
    def __init__(self, seq_quote: _Optional[_Union[_seqquote_pb2.SeqQuote, _Mapping]] = ...) -> None: ...

class OnUpdateTradeOrder_Msg(_message.Message):
    __slots__ = ("trade_order", "trading_fee")
    TRADE_ORDER_FIELD_NUMBER: _ClassVar[int]
    TRADING_FEE_FIELD_NUMBER: _ClassVar[int]
    trade_order: _order_pb2.Order
    trading_fee: _orderfee_pb2.OrderFee
    def __init__(self, trade_order: _Optional[_Union[_order_pb2.Order, _Mapping]] = ..., trading_fee: _Optional[_Union[_orderfee_pb2.OrderFee, _Mapping]] = ...) -> None: ...

class OnUpdateMktSession_Msg(_message.Message):
    __slots__ = ("mkt_session",)
    MKT_SESSION_FIELD_NUMBER: _ClassVar[int]
    mkt_session: str
    def __init__(self, mkt_session: _Optional[str] = ...) -> None: ...

class OnUpdateStockSnapshots_Msg(_message.Message):
    __slots__ = ("stock_snapshots",)
    STOCK_SNAPSHOTS_FIELD_NUMBER: _ClassVar[int]
    stock_snapshots: _containers.RepeatedCompositeFieldContainer[_stocksnapshot_pb2.StockSnapshot]
    def __init__(self, stock_snapshots: _Optional[_Iterable[_Union[_stocksnapshot_pb2.StockSnapshot, _Mapping]]] = ...) -> None: ...

class QueryRTSnapshots_Req(_message.Message):
    __slots__ = ("code_lst",)
    CODE_LST_FIELD_NUMBER: _ClassVar[int]
    code_lst: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, code_lst: _Optional[_Iterable[str]] = ...) -> None: ...

class QueryRTSnapshots_Res(_message.Message):
    __slots__ = ("code", "active_orders", "holdings", "prev_close", "histo_deals", "histo_fees", "seq_quotes")
    CODE_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_ORDERS_FIELD_NUMBER: _ClassVar[int]
    HOLDINGS_FIELD_NUMBER: _ClassVar[int]
    PREV_CLOSE_FIELD_NUMBER: _ClassVar[int]
    HISTO_DEALS_FIELD_NUMBER: _ClassVar[int]
    HISTO_FEES_FIELD_NUMBER: _ClassVar[int]
    SEQ_QUOTES_FIELD_NUMBER: _ClassVar[int]
    code: str
    active_orders: _containers.RepeatedCompositeFieldContainer[_order_pb2.Order]
    holdings: _containers.RepeatedCompositeFieldContainer[_position_pb2.Position]
    prev_close: float
    histo_deals: _containers.RepeatedCompositeFieldContainer[_deal_pb2.Deal]
    histo_fees: _containers.RepeatedCompositeFieldContainer[_orderfee_pb2.OrderFee]
    seq_quotes: _containers.RepeatedCompositeFieldContainer[_seqquote_pb2.SeqQuote]
    def __init__(self, code: _Optional[str] = ..., active_orders: _Optional[_Iterable[_Union[_order_pb2.Order, _Mapping]]] = ..., holdings: _Optional[_Iterable[_Union[_position_pb2.Position, _Mapping]]] = ..., prev_close: _Optional[float] = ..., histo_deals: _Optional[_Iterable[_Union[_deal_pb2.Deal, _Mapping]]] = ..., histo_fees: _Optional[_Iterable[_Union[_orderfee_pb2.OrderFee, _Mapping]]] = ..., seq_quotes: _Optional[_Iterable[_Union[_seqquote_pb2.SeqQuote, _Mapping]]] = ...) -> None: ...

class BaseQuote(_message.Message):
    __slots__ = ("code", "prev_close")
    CODE_FIELD_NUMBER: _ClassVar[int]
    PREV_CLOSE_FIELD_NUMBER: _ClassVar[int]
    code: str
    prev_close: float
    def __init__(self, code: _Optional[str] = ..., prev_close: _Optional[float] = ...) -> None: ...

class OnBasicSync_Req(_message.Message):
    __slots__ = ("code_lst",)
    CODE_LST_FIELD_NUMBER: _ClassVar[int]
    code_lst: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, code_lst: _Optional[_Iterable[str]] = ...) -> None: ...

class OnBasicSync_Res(_message.Message):
    __slots__ = ("mkt_session", "base_quotes")
    MKT_SESSION_FIELD_NUMBER: _ClassVar[int]
    BASE_QUOTES_FIELD_NUMBER: _ClassVar[int]
    mkt_session: str
    base_quotes: _containers.RepeatedCompositeFieldContainer[BaseQuote]
    def __init__(self, mkt_session: _Optional[str] = ..., base_quotes: _Optional[_Iterable[_Union[BaseQuote, _Mapping]]] = ...) -> None: ...

class OnTradeDeal_Req(_message.Message):
    __slots__ = ("code_lst",)
    CODE_LST_FIELD_NUMBER: _ClassVar[int]
    code_lst: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, code_lst: _Optional[_Iterable[str]] = ...) -> None: ...

class OnTradeDeal_Res(_message.Message):
    __slots__ = ("code", "trade_deal", "new_holding", "trading_fee")
    CODE_FIELD_NUMBER: _ClassVar[int]
    TRADE_DEAL_FIELD_NUMBER: _ClassVar[int]
    NEW_HOLDING_FIELD_NUMBER: _ClassVar[int]
    TRADING_FEE_FIELD_NUMBER: _ClassVar[int]
    code: str
    trade_deal: _deal_pb2.Deal
    new_holding: _position_pb2.Position
    trading_fee: _orderfee_pb2.OrderFee
    def __init__(self, code: _Optional[str] = ..., trade_deal: _Optional[_Union[_deal_pb2.Deal, _Mapping]] = ..., new_holding: _Optional[_Union[_position_pb2.Position, _Mapping]] = ..., trading_fee: _Optional[_Union[_orderfee_pb2.OrderFee, _Mapping]] = ...) -> None: ...

class OnOrderBook_Req(_message.Message):
    __slots__ = ("code_lst",)
    CODE_LST_FIELD_NUMBER: _ClassVar[int]
    code_lst: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, code_lst: _Optional[_Iterable[str]] = ...) -> None: ...

class OnSeqQuote_Req(_message.Message):
    __slots__ = ("code_lst",)
    CODE_LST_FIELD_NUMBER: _ClassVar[int]
    code_lst: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, code_lst: _Optional[_Iterable[str]] = ...) -> None: ...
