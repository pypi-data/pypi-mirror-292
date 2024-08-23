# LOCK-BEGIN[imports]: DON'T MODIFY
from podite import (
    U128,
    U64,
    pod,
)
from solders.pubkey import Pubkey

# LOCK-END


# LOCK-BEGIN[class(CallBackInfo)]: DON'T MODIFY
@pod
class CallBackInfo:
    user_account: Pubkey
    open_orders_idx: U64
    order_nonce: U128
    client_order_id: U64
    # LOCK-END

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)
