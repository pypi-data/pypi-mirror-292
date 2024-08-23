# LOCK-BEGIN[imports]: DON'T MODIFY
from dexteritysdk.codegen.dex.types.fractional import Fractional
from dexteritysdk.codegen.dex.types.product_metadata import ProductMetadata
from dexteritysdk.codegen.dex.types.product_status import ProductStatus
from dexteritysdk.solmate.dtypes import Usize
from podite import (
    FixedLenArray,
    U64,
    pod,
)

# LOCK-END


# LOCK-BEGIN[class(Outright)]: DON'T MODIFY
@pod
class Outright:
    metadata: "ProductMetadata"
    num_risk_state_accounts: Usize
    product_status: "ProductStatus"
    dust: "Fractional"
    cum_funding_per_share: "Fractional"
    cum_social_loss_per_share: "Fractional"
    open_long_interest: "Fractional"
    open_short_interest: "Fractional"
    mark_price_qualifying_cum_value: "Fractional"
    mark_price_max_qualifying_width: "Fractional"
    padding: FixedLenArray[U64, 10]
    # LOCK-END

    def is_expired(self) -> bool:
        return self.product_status == ProductStatus.EXPIRED

    def is_active(self) -> bool:
        return self.product_status != ProductStatus.UNINITIALIZED

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)
