# LOCK-BEGIN[imports]: DON'T MODIFY
from dexteritysdk.codegen.dex.types.fractional import Fractional
from dexteritysdk.codegen.dex.types.order_type import OrderType
from dexteritysdk.utils.aob.state.base import (
    SelfTradeBehavior,
    Side,
)
from podite import (
    U64,
    pod,
)

# LOCK-END


# LOCK-BEGIN[class(NewOrderParams)]: DON'T MODIFY
@pod
class NewOrderParams:
    side: Side
    max_base_qty: Fractional
    order_type: "OrderType"
    self_trade_behavior: SelfTradeBehavior
    match_limit: U64
    limit_price: Fractional
    referrer_fee_bps: Fractional
    client_order_id: U64
    # LOCK-END

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)
