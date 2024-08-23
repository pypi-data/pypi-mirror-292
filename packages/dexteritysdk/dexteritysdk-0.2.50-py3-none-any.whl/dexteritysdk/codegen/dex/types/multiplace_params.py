# LOCK-BEGIN[imports]: DON'T MODIFY
from dexteritysdk.codegen.dex.types.fractional import Fractional
from dexteritysdk.codegen.dex.types.multiplace_param import MultiplaceParam
from dexteritysdk.utils.aob.state.base import SelfTradeBehavior
from podite import (
    U64,
    U8,
    pod,
)

# LOCK-END


# LOCK-BEGIN[class(MultiplaceParams)]: DON'T MODIFY
@pod
class MultiplaceParams:
    match_limit: U64
    referrer_fee_bps: Fractional
    self_trade_behavior: SelfTradeBehavior
    num_new_orders: U8
    new_order0: "MultiplaceParam"
    new_order1: "MultiplaceParam"
    new_order2: "MultiplaceParam"
    new_order3: "MultiplaceParam"
    new_order4: "MultiplaceParam"
    new_order5: "MultiplaceParam"
    new_order6: "MultiplaceParam"
    new_order7: "MultiplaceParam"
    new_order8: "MultiplaceParam"
    new_order9: "MultiplaceParam"
    new_order10: "MultiplaceParam"
    new_order11: "MultiplaceParam"
    # LOCK-END

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)
