# LOCK-BEGIN[imports]: DON'T MODIFY
from dexteritysdk.codegen.dex.types.fractional import Fractional
from dexteritysdk.codegen.instruments.types.account_tag import AccountTag
from dexteritysdk.codegen.instruments.types.expiration_status import ExpirationStatus
from dexteritysdk.codegen.instruments.types.instrument_type import InstrumentType
from dexteritysdk.codegen.instruments.types.oracle_type import OracleType
from dexteritysdk.solmate.dtypes import UnixTimestamp
from podite import (
    U64,
    pod,
)
from solders.pubkey import Pubkey

# LOCK-END


# LOCK-BEGIN[class(DerivativeMetadata)]: DON'T MODIFY
@pod
class DerivativeMetadata:
    tag: AccountTag
    expiration_status: ExpirationStatus
    oracle_type: OracleType
    instrument_type: InstrumentType
    bump: U64
    strike: Fractional
    initialization_time: UnixTimestamp
    full_funding_period: UnixTimestamp
    minimum_funding_period: UnixTimestamp
    price_oracle: Pubkey
    market_product_group: Pubkey
    close_authority: Pubkey
    clock: Pubkey
    last_funding_time: UnixTimestamp
    # LOCK-END

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)
