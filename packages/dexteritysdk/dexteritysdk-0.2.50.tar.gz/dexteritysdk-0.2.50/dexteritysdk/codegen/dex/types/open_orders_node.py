# LOCK-BEGIN[imports]: DON'T MODIFY
from podite import (
    U128,
    U16,
    U64,
    pod,
    U32,
)

# LOCK-END


# LOCK-BEGIN[class(OpenOrdersNode)]: DON'T MODIFY
@pod
class OpenOrdersNode:
    id: U128
    qty: U64
    client_id: U64
    prev: U16
    next: U16
    padding: U32
    # LOCK-END

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)
