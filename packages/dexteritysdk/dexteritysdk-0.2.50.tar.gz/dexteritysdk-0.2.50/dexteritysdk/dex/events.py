from dataclasses import dataclass
from enum import Enum
from typing import Union

from anchorpy import Event
from solders.pubkey import Pubkey

from dexteritysdk.utils.aob.state import Side
from decimal import *

class CompletedReason(Enum):
    Cancelled = 0
    Filled = 1
    Booted = 2
    SelfTradeCancel = 3
    PostNotAllowed = 4
    MatchLimitExhausted = 5
    PostOnly = 6
    Expired = 7


def decimal_from_int(num) -> Decimal:
    return Decimal(num).scaleb(-8)

def bps_from_int(num) -> Decimal:
    return Decimal(num).scaleb(-4)


@dataclass
class OrderPlacedEvent:
    market_product_group: Pubkey
    trader_risk_group: Pubkey
    product: str
    order_id: int
    client_order_id: int
    side: Side
    price: Decimal
    size: Decimal
    filled_size: Decimal
    posted_size: Decimal
    referrer_trader_risk_group: Pubkey
    referrer_fee_bps: Decimal

    @classmethod
    def from_event(cls, event: Event):
        assert event.name == cls.__name__
        return cls(
            market_product_group=event.data.market_product_group,
            trader_risk_group=event.data.trader_risk_group,
            product=bytes(event.data.product).decode("utf-8").strip(),
            order_id=event.data.order_id,
            client_order_id=event.data.client_order_id,
            side=Side(event.data.side.index),
            price=decimal_from_int(event.data.price),
            size=decimal_from_int(event.data.size),
            filled_size=decimal_from_int(event.data.filled_size),
            posted_size=decimal_from_int(event.data.posted_size),
            referrer_trader_risk_group=event.data.referrer_trader_risk_group,
            referrer_fee_bps=bps_from_int(event.data.referrer_fee_bps),
        )


@dataclass
class OrderFillEvent:
    market_product_group: Pubkey
    product: str
    maker_trader_risk_group: Pubkey
    maker_order_id: int
    maker_order_nonce: int
    maker_client_order_id: int
    maker_fee: Decimal
    taker_trader_risk_group: Pubkey
    taker_order_id: int
    taker_order_nonce: int
    taker_client_order_id: int
    taker_fee: Decimal
    taker_side: Side
    price: Decimal
    base_size: Decimal
    quote_size: Decimal

    @classmethod
    def from_event(cls, event: Event):
        assert event.name == cls.__name__
        return cls(
            market_product_group=event.data.market_product_group,
            product=bytes(event.data.product).decode("utf-8").strip(),
            maker_trader_risk_group=event.data.maker_trader_risk_group,
            maker_order_id=event.data.maker_order_id,
            maker_order_nonce=event.data.maker_order_nonce,
            maker_client_order_id=event.data.maker_client_order_id,
            maker_fee=decimal_from_int(event.data.maker_fee),
            taker_trader_risk_group=event.data.taker_trader_risk_group,
            taker_order_id=event.data.taker_order_id,
            taker_order_nonce=event.data.taker_order_nonce,
            taker_client_order_id=event.data.taker_client_order_id,
            taker_fee=decimal_from_int(event.data.taker_fee),
            taker_side=Side(event.data.taker_side.index),
            price=decimal_from_int(event.data.price),
            base_size=decimal_from_int(event.data.base_size),
            quote_size=decimal_from_int(event.data.quote_size),
        )


@dataclass
class OrderCompletedEvent:
    market_product_group: Pubkey
    trader_risk_group: Pubkey
    product: str
    order_id: int
    client_order_id: int
    side: Side
    size: Decimal
    reason: CompletedReason

    @classmethod
    def from_event(cls, event: Event):
        assert event.name == cls.__name__
        return cls(
            market_product_group=event.data.market_product_group,
            trader_risk_group=event.data.trader_risk_group,
            product=bytes(event.data.product).decode("utf-8").strip(),
            order_id=event.data.order_id,
            client_order_id=event.data.client_order_id,
            side=Side(event.data.side.index),
            size=decimal_from_int(event.data.size),
            reason=CompletedReason(event.data.reason.index)
        )


@dataclass
class OrderCancelledEvent:
    market_product_group: Pubkey
    trader_risk_group: Pubkey
    product: str
    order_id: int
    client_order_id: int
    side: Side
    size: Decimal

    @classmethod
    def from_event(cls, event: Event):
        assert event.name == cls.__name__
        return cls(
            market_product_group=event.data.market_product_group,
            trader_risk_group=event.data.trader_risk_group,
            product=bytes(event.data.product).decode("utf-8").strip(),
            order_id=event.data.order_id,
            client_order_id=event.data.client_order_id,
            side=Side(event.data.side.index),
            size=decimal_from_int(event.data.size),
        )


@dataclass
class TraderApplyFundingEvent:
    market_product_group: Pubkey
    trader_risk_group: Pubkey
    product: str
    funding_amount: Decimal
    social_loss_amount: Decimal
    remaining_cash_balance: Decimal

    @classmethod
    def from_event(cls, event: Event):
        assert event.name == cls.__name__
        return cls(
            market_product_group=event.data.market_product_group,
            trader_risk_group=event.data.trader_risk_group,
            product=bytes(event.data.product).decode("utf-8").strip(),
            funding_amount=decimal_from_int(event.data.funding_amount),
            social_loss_amount=decimal_from_int(event.data.social_loss_amount),
            remaining_cash_balance=decimal_from_int(event.data.remaining_cash_balance),
        )


@dataclass
class TraderDepositEvent:
    market_product_group: Pubkey
    trader_risk_group: Pubkey
    qty: Decimal

    @classmethod
    def from_event(cls, event: Event):
        assert event.name == cls.__name__
        return cls(
            market_product_group=event.data.market_product_group,
            trader_risk_group=event.data.trader_risk_group,
            qty=decimal_from_int(event.data.qty),
        )


@dataclass
class TraderWithdrawalEvent:
    market_product_group: Pubkey
    trader_risk_group: Pubkey
    qty: Decimal

    @classmethod
    def from_event(cls, event: Event):
        assert event.name == cls.__name__
        return cls(
            market_product_group=event.data.market_product_group,
            trader_risk_group=event.data.trader_risk_group,
            qty=decimal_from_int(event.data.qty),
        )


@dataclass
class TraderLiquidationEvent:
    market_product_group: Pubkey
    liquidator_trader_risk_group: Pubkey
    liquidatee_trader_risk_group: Pubkey
    liquidator_cash_balance: Decimal
    liquidatee_cash_balance: Decimal
    liquidation_price: Decimal

    @classmethod
    def from_event(cls, event: Event):
        assert event.name == cls.__name__
        return cls(
            market_product_group=event.data.market_product_group,
            liquidator_trader_risk_group=event.data.liquidator_trader_risk_group,
            liquidatee_trader_risk_group=event.data.liquidatee_trader_risk_group,
            liquidator_cash_balance=decimal_from_int(event.data.liquidator_cash_balance),
            liquidatee_cash_balance=decimal_from_int(event.data.liquidatee_cash_balance),
            liquidation_price=decimal_from_int(event.data.liquidation_price),
        )


DexEvent = Union[OrderPlacedEvent, OrderCompletedEvent, OrderFillEvent, OrderCancelledEvent, TraderLiquidationEvent,
                 TraderWithdrawalEvent, TraderDepositEvent, TraderApplyFundingEvent]
