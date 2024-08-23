# LOCK-BEGIN[imports]: DON'T MODIFY
from dexteritysdk.codegen.dex.types.account_tag import AccountTag
from dexteritysdk.codegen.dex.types.fractional import Fractional
from dexteritysdk.codegen.dex.types.locked_collateral import LockedCollateral
from dexteritysdk.codegen.dex.types.open_orders import OpenOrders
from dexteritysdk.codegen.dex.types.trader_position import TraderPosition
from dexteritysdk.solmate.dtypes import UnixTimestamp
from podite import (
    FixedLenArray,
    I32,
    U8,
    pod,
)
from solders.pubkey import Pubkey

# LOCK-END


# LOCK-BEGIN[class(TraderRiskGroup)]: DON'T MODIFY
@pod
class TraderRiskGroup:
    tag: AccountTag
    market_product_group: Pubkey
    owner: Pubkey
    active_products: FixedLenArray[U8, 128]
    total_deposited: Fractional
    total_withdrawn: Fractional
    cash_balance: Fractional
    pending_cash_balance: Fractional
    pending_fees: Fractional
    valid_until: UnixTimestamp
    maker_fee_bps: I32
    taker_fee_bps: I32
    trader_positions: FixedLenArray[TraderPosition, 16]
    risk_state_account: Pubkey
    fee_state_account: Pubkey
    locked_collateral: FixedLenArray[LockedCollateral, 16]
    notional_maker_volume: Fractional
    notional_taker_volume: Fractional
    referred_makers_notional_volume: Fractional
    referred_takers_notional_volume: Fractional
    referral_fees: Fractional
    allocated_for_future_use: FixedLenArray[U8, 256]
    open_orders: OpenOrders
    # LOCK-END

    @classmethod
    def to_bytes(cls, obj, **kwargs):
        return cls.pack(obj, converter="bytes", **kwargs)

    @classmethod
    def from_bytes(cls, raw, **kwargs):
        return cls.unpack(raw, converter="", **kwargs)
