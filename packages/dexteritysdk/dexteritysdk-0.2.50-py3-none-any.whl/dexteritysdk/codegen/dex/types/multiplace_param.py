# LOCK-BEGIN[imports]: DON'T MODIFY
from dexteritysdk.codegen.dex.types.fractional import Fractional
from dexteritysdk.codegen.dex.types.order_type import OrderType
from dexteritysdk.utils.aob.state.base import Side
from podite import (
    U64,
    pod,
)

# LOCK-END


# LOCK-BEGIN[class(MultiplaceParam)]: DON'T MODIFY
@pod
class MultiplaceParam:
    side: Side
    max_base_qty: Fractional
    limit_price: Fractional
    client_order_id: U64
    order_type: "OrderType"
    # LOCK-END

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)
