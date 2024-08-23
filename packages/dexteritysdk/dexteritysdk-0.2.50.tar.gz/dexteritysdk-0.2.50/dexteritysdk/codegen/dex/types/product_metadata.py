# LOCK-BEGIN[imports]: DON'T MODIFY
from dexteritysdk.codegen.dex.types.fractional import Fractional
from dexteritysdk.codegen.dex.types.price_ewma import PriceEwma
from podite import (
    FixedLenArray,
    U64,
    U8,
    pod,
)
from solders.pubkey import Pubkey

# LOCK-END


# LOCK-BEGIN[class(ProductMetadata)]: DON'T MODIFY
@pod
class ProductMetadata:
    bump: U64
    product_key: Pubkey
    name: FixedLenArray[U8, 16]
    orderbook: Pubkey
    tick_size: "Fractional"
    base_decimals: U64
    price_offset: "Fractional"
    notional_traded_volume: "Fractional"
    prices: PriceEwma
    # LOCK-END

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)
