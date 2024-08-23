# LOCK-BEGIN[imports]: DON'T MODIFY
from dexteritysdk.codegen.dex.types.account_tag import AccountTag
from dexteritysdk.codegen.dex.types.bitset import Bitset
from dexteritysdk.codegen.dex.types.fractional import Fractional
from dexteritysdk.codegen.dex.types.product_array import ProductArray
from podite import (
    FixedLenArray,
    I16,
    U128,
    U16,
    U64,
    U8,
    pod,
)
from solders.pubkey import Pubkey

# LOCK-END

from collections.abc import Iterable
from dexteritysdk.codegen.dex import types


# LOCK-BEGIN[class(MarketProductGroup)]: DON'T MODIFY
@pod
class MarketProductGroup:
    tag: AccountTag
    name: FixedLenArray[U8, 16]
    authority: Pubkey
    successor: Pubkey
    vault_mint: Pubkey
    collected_fees: Fractional
    fee_collector: Pubkey
    decimals: U64
    risk_engine_program_id: Pubkey
    fee_model_program_id: Pubkey
    fee_model_configuration_acct: Pubkey
    risk_model_configuration_acct: Pubkey
    active_flags_products: Bitset
    ewma_windows: FixedLenArray[U64, 4]
    market_products: "ProductArray"
    vault_bump: U16
    risk_and_fee_bump: U16
    find_fees_discriminant_len: U16
    validate_account_discriminant_len: U16
    find_fees_discriminant: FixedLenArray[U8, 8]
    validate_account_health_discriminant: FixedLenArray[U8, 8]
    validate_account_liquidation_discriminant: FixedLenArray[U8, 8]
    create_risk_state_account_discriminant: FixedLenArray[U8, 8]
    max_maker_fee_bps: I16
    min_maker_fee_bps: I16
    max_taker_fee_bps: I16
    min_taker_fee_bps: I16
    fee_output_register: Pubkey
    risk_output_register: Pubkey
    sequence_number: U128
    staking_fee_collector: Pubkey
    is_killed: bool
    create_fee_state_account_discriminant: FixedLenArray[U8, 8]
    address_lookup_table: Pubkey
    close_risk_state_account_discriminant: FixedLenArray[U8, 8]
    close_fee_state_account_discriminant: FixedLenArray[U8, 8]
    is_admin_mode: bool
    # LOCK-END

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="bytes", **kwargs)

    def active_products(self) -> Iterable[int, "types.Product"]:
        for idx, p in enumerate(self.market_products.array):
            if self.is_active(p):
                yield idx, p

    def is_active(self, product: "types.Product") -> bool:
        for p in self.market_products.array:
            if p.metadata().product_key != product.metadata().product_key:
                continue
            if p.is_outright():
                return p.field.outright.is_active()
            else:
                return all(
                    map(
                        lambda leg: self.market_products.array[leg.product_index].field.outright.is_active(),
                        p.field.combo.legs_array
                    )
                )

    def is_expired(self, product: "types.Product") -> bool:
        for p in self.market_products.array:
            if p.metadata().product_key != product.metadata().product_key:
                continue
            if p.is_outright():
                return p.field.outright.is_expired()
            else:
                return any(
                    map(
                        lambda leg: self.market_products.array[leg.product_index].field.outright.is_expired() or
                                    not self.market_products.array[leg.product_index].field.outright.is_active(),
                        p.field.combo.legs_array
                    )
                )


SENTINAL_KEY = Pubkey.from_string("11111111111111111111111111111111")
