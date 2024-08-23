# LOCK-BEGIN[imports]: DON'T MODIFY
from dexteritysdk.codegen.dex.types.fractional import Fractional
from dexteritysdk.codegen.dex.types.operation_type import OperationType
from dexteritysdk.solmate.dtypes import Usize
from dexteritysdk.utils.aob.state.base import Side
from podite import pod

# LOCK-END


# LOCK-BEGIN[class(OrderInfo)]: DON'T MODIFY
@pod
class OrderInfo:
    total_order_qty: "Fractional"
    matched_order_qty: "Fractional"
    order_side: Side
    order_price: "Fractional"
    is_combo: bool
    product_index: Usize
    operation_type: "OperationType"
    old_ask_qty_in_book: "Fractional"
    old_bid_qty_in_book: "Fractional"
    # LOCK-END

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)
