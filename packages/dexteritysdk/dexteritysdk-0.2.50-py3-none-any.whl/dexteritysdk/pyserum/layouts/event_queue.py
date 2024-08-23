from __future__ import annotations
from enum import IntEnum
from construct import Bytes
from construct import Switch
from borsh_construct import CStruct, U8, U64, U128, Bool

CALLBACK = CStruct(
    "account" / Bytes(32),
    "open_orders_idx" / U64,
    "order_nonce" / U128,
    "client_order_id" / U64,
)

EVENT_QUEUE_HEADER_LAYOUT = CStruct(
    "tag" / U8,
    "head" / U64,
    "count" / U64,
    "event_size" / U64,
    "seq_num" / U64,
)

# Option[OrderSummary]
REGISTER = CStruct(
    "register_present" / Bool,
    # Option[U128]
    "posted_order_id_present" / Bool,
    "posted_order_id" / U128,
    "total_base_qty" / U64,
    "total_quote_qty" / U64,
    "total_base_qty_posted" / U64,
)


class EventType(IntEnum):
    FILL = 0
    OUT = 1


class Side(IntEnum):
    BID = 0
    ASK = 1


class CompletedReason(IntEnum):
    CANCELLED = 0
    FILLED = 1
    BOOTED = 2
    SELF_TRADE_CANCEL = 3
    POST_NOT_ALLOWED = 4
    MATCH_LIMIT_EXHAUSTED = 5
    POST_ONLY = 6


# events
FILL_EVENT = CStruct(
    "taker_side" / U8,
    "maker_order_id" / U128,
    "quote_size" / U64,
    "base_size" / U64,
    "maker_callback" / CALLBACK,
    "taker_callback" / CALLBACK,
)

OUT_EVENT = CStruct(
    "side" / U8,
    "order_id" / U128,
    "base_size" / U64,
    "delete" / Bool,
    "callback" / CALLBACK,
    "reason" / U8,
)

EVENT_NODE_LAYOUT = CStruct(
    "tag" / U8,
    "data"
    / Switch(
        lambda this: this.tag,
        {
            EventType.FILL: FILL_EVENT,
            EventType.OUT: OUT_EVENT,
        },
    ),
)
