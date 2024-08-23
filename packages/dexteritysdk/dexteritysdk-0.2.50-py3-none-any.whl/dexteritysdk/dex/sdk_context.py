import base64
import threading
import os

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from typing import Any, Callable, List, Optional, Tuple, Union

import base58
import lz4.block
from borsh_construct import CStruct, U64, U32, U8
from solana.rpc import commitment, types
from solana.rpc.commitment import Confirmed
from solana.rpc.websocket_api import connect as solana_ws_connect
from solders.rpc.config import RpcTransactionLogsFilterMentions

from dexteritysdk.dex.events import OrderPlacedEvent, DexEvent, TraderDepositEvent, TraderWithdrawalEvent, \
    OrderCancelledEvent, OrderFillEvent, OrderCompletedEvent, TraderLiquidationEvent, TraderApplyFundingEvent, \
    CompletedReason
from solana.transaction import Instruction
from solders import system_program
from solders.address_lookup_table_account import AddressLookupTableAccount
from solders.instruction import AccountMeta
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.rpc.responses import AccountNotification, SubscriptionResult, SubscriptionError, LogsNotification
from spl.token import instructions as spl_token_instructions

import dexteritysdk.codegen.dex.instructions as dixs
import dexteritysdk.codegen.dex.types as dtys
import dexteritysdk.codegen.risk_engine.instructions as rixs
from dexteritysdk import program_ids as pids, mints
from dexteritysdk.codegen.dex.accounts import Accounts as DexAccounts
from dexteritysdk.codegen.dex.constants import SENTINEL
from dexteritysdk.codegen.dex.types import MarketProductGroup, CancelOrderParams, ProductMetadata, account_tag
from dexteritysdk.codegen.instruments.accounts import Accounts as InstrumentAccounts
from dexteritysdk.codegen.instruments.types import DerivativeMetadata
from dexteritysdk.codegen.risk_engine.accounts import Accounts as RiskEngineAccounts
from dexteritysdk.codegen.risk_engine.types import MarkPricesArray, UpdateMarkPricesParams
from dexteritysdk.pyserum.orderbook import OrderBook
from dexteritysdk.dex import addrs as daddrs
from dexteritysdk.utils import solana as solana_utils
from dexteritysdk.utils.aob import state as aaob_state
from dexteritysdk.utils.solana import Client, Context, AccountParser, explore, fetch_account_details, explore_many
from dexteritysdk.solmate.utils import to_account_meta

from anchorpy import EventParser, Idl, Program, Provider

idl_path = os.path.join(os.path.dirname(__file__), "../idl/dex.json")
with open(idl_path, "r") as f:
    idl = Idl.from_json(f.read())

DEFAULT_MATCH_LIMIT = 16


class DexEventNotFound(Exception):
    pass


class SDKEventType(Enum):
    SNAPSHOT = 1
    NEW = 2
    UPDATED = 3
    CLOSED = 4
    CANCELLED = 5
    FILLED = 6


@dataclass
class SDKFill:
    product: "SDKProduct"
    maker_order_id: int
    taker_order_id: int
    taker_side: aaob_state.Side
    qty: float
    price: float
    quote_qty: float
    maker_trader_risk_group: Pubkey
    taker_trader_risk_group: Pubkey
    maker_order_nonce: int
    taker_order_nonce: int
    maker_fee: float
    taker_fee: float
    is_maker: bool


@dataclass
class SDKPosition:
    product: "SDKProduct"
    position: float
    pending_position: float
    last_cum_funding_snapshot: float
    last_social_loss_snapshot: float


@dataclass
class SDKOrder:
    order_id: int
    product: "SDKProduct"
    side: aaob_state.Side
    price: float
    qty: float
    client_order_id: int
    trader_risk_group: Pubkey

    @staticmethod
    def from_pyserum_orderbook(order_book: OrderBook, product: "SDKProduct", bids: bool, slot: int) -> List["SDKOrder"]:
        return [
            SDKOrder(
                o.order_id,
                product,
                aaob_state.Side.BID if bids else aaob_state.Side.ASK,
                o.info.price,
                o.info.size,
                o.client_id,
                Pubkey.from_bytes(o.info.trader),
            ) for o in order_book.orders() if o.info.expiration_slot == 0 or o.info.expiration_slot > slot
        ]


@dataclass
class MultiplaceOrder:
    side: aaob_state.Side
    size: Union[dtys.Fractional, float]
    price: Union[dtys.Fractional, float]
    order_type: dtys.OrderType = dtys.OrderType.LIMIT
    client_order_id: int = 0


@dataclass
class SDKProduct:
    key: Pubkey
    index: int
    name: str  # max 16 bytes
    orderbook: Pubkey
    bids: Pubkey
    asks: Pubkey
    market_signer: Pubkey
    event_queue: Pubkey
    metadata: ProductMetadata  # last time prod was fetched
    price_oracle: Pubkey
    is_combo: bool
    _orderbook_data: "SDKOrderBook" = None

    def __hash__(self):
        return self.key.__hash__()

    def get_orderbook(self, sdk: "SDKContext", refresh: bool = False) -> "SDKOrderBook":
        if refresh or self._orderbook_data is None:
            self._orderbook_data = SDKOrderBook.from_product(sdk, self)
        return self._orderbook_data

    def crank_raw(self, sdk: "SDKContext", trader_and_risk_accounts: List[Pubkey], reward_target: Pubkey):
        trader_and_risk_accounts.sort()
        trader_and_risk_accounts = _dedup(trader_and_risk_accounts)
        ix = dixs.consume_orderbook_events(
            aaob_program=sdk.aaob_program,
            market_product_group=sdk.market_product_group,
            product=self.key,
            market_signer=self.market_signer,
            orderbook=self.orderbook,
            event_queue=self.event_queue,
            reward_target=reward_target,
            fee_model_program=sdk.fee_model_program,
            fee_model_configuration_acct=sdk.fee_model_configuration_acct,
            fee_output_register=sdk.fee_output_register,
            risk_and_fee_signer=daddrs.get_risk_signer(sdk.market_product_group),
            params=dtys.ConsumeOrderbookEventsParams(
                20
            ),
            remaining_accounts=[AccountMeta(pk, False, False) for pk in trader_and_risk_accounts]
        )
        solana_utils.send_instructions(ix)


def _dedup(xs):
    if len(xs) < 2:
        return xs
    i = 0
    for acct in xs[1:]:
        if xs[i] != acct:
            i += 1
            xs[i] = acct
    return xs[:i + 1]


@dataclass
class SDKOrderBook:
    product: SDKProduct
    bids: List[SDKOrder]
    asks: List[SDKOrder]
    slot: int

    @staticmethod
    def from_product(sdk: "SDKContext", product: "SDKProduct", filter_expired=True) -> "SDKOrderBook":
        ob_data = explore_many([product.bids, product.asks])
        bids_data = ob_data.data[0]
        asks_data = ob_data.data[1]
        slot = ob_data.slot if filter_expired else 0

        return SDKOrderBook(
            product=product,
            bids=SDKOrder.from_pyserum_orderbook(
                order_book=OrderBook.from_bytes(bids_data, product.metadata.base_decimals,
                                                product.metadata.price_offset, product.metadata.tick_size),
                product=product,
                bids=True,
                slot=slot,
            ),
            asks=SDKOrder.from_pyserum_orderbook(
                order_book=OrderBook.from_bytes(asks_data, product.metadata.base_decimals,
                                                product.metadata.price_offset, product.metadata.tick_size),
                product=product,
                bids=False,
                slot=slot,
            ),
            slot=ob_data.slot,
        )

    def find_order(self, order_id: int) -> SDKOrder:
        bid_match = next((o for o in self.bids if o.order_id == order_id), None)
        return bid_match if bid_match is not None else next((o for o in self.asks if o.order_id == order_id), None)


@dataclass
class _PendingNewOrder:
    product: Union[SDKProduct, Pubkey]
    side: aaob_state.Side
    size: Union[dtys.Fractional, float]
    price: Union[dtys.Fractional, float]
    self_trade_behavior: aaob_state.SelfTradeBehavior
    order_type: dtys.OrderType
    match_limit: int
    expiration_slot: int


def _extract_multiplace_param(orders, index) -> dtys.MultiplaceParam:
    if len(orders) > index:
        order = orders[index]
        return dtys.MultiplaceParam(
            side=order.side,
            max_base_qty=dtys.Fractional.into(order.size, 8).simplify(),
            limit_price=dtys.Fractional.into(order.price, 8).simplify(),
            order_type=order.order_type,
            client_order_id=order.client_order_id,
        )
    return dtys.MultiplaceParam(
        side=aaob_state.Side.BID,
        max_base_qty=dtys.Fractional(0, 0),
        limit_price=dtys.Fractional(0, 0),
        order_type=dtys.OrderType.LIMIT,
        client_order_id=0,
    )


@dataclass
class SDKTrader:
    keypair: Keypair
    account: Pubkey
    wallet: Pubkey
    trader_fee_state_acct: Pubkey
    trader_risk_state_acct: Pubkey  # separate pk vs kp to allow **vars(trader) in ixs
    whitelist_token_wallet: Pubkey
    staker_state: Pubkey

    _batches_lock: threading.Lock
    _batch_id: int
    _pending_batches: dict

    async def _monitor_accounts(
        self,
        sdk: "SDKContext",
        url: str,
        positions_callback: Callable[[List[SDKPosition], SDKEventType], Any],
        orders_callback: Callable[[List[SDKOrder], SDKEventType], Any],
        fills_callback: Callable[[List[SDKFill], SDKEventType], Any]
    ):
        async for ws in solana_ws_connect(url):
            try:
                trg, trg_slot = self.get_trader_risk_group()

                positions = None
                if positions_callback:
                    positions = list(self.open_positions(sdk, trg=trg))
                    positions_callback(positions, SDKEventType.SNAPSHOT)

                open_order_ids = defaultdict(set)
                if orders_callback:
                    open_orders = list(self.open_orders(sdk, trg=trg))
                    orders_callback(open_orders, SDKEventType.SNAPSHOT)
                    for o in open_orders:
                        open_order_ids[o.product].add(o.order_id)

                await ws.account_subscribe(self.account, commitment=commitment.Confirmed, encoding="base64")
                await ws.logs_subscribe(RpcTransactionLogsFilterMentions(self.account), commitment=commitment.Confirmed)

                async for msgs in ws:
                    for msg in msgs:
                        if isinstance(msg, SubscriptionResult):
                            if msg.id == 1:
                                print(f"Successfully subscribed to TRG account updates [account={self.account}]")
                            else:
                                print(f"Successfully subscribed to TRG logs [mentions={self.account}]")
                        elif isinstance(msg, SubscriptionError):
                            raise ValueError(f"Failed to subscribe [account={self.account}, exc={msg}]")
                        elif isinstance(msg, AccountNotification):
                            data = msg.result.value.data
                            trg = DexAccounts.from_bytes(data).field

                            if positions_callback:
                                new_positions = list(self.open_positions(sdk, trg))
                                for position in positions:
                                    new_position = next(
                                        (p for p in new_positions if p.product == position.product),
                                        None
                                    )
                                    # if position was closed
                                    if not new_position:
                                        positions_callback([SDKPosition(position.product, 0, 0, 0, 0)],
                                                           SDKEventType.CLOSED)
                                    # if existing position has changed
                                    elif position != new_position:
                                        positions_callback([new_position], SDKEventType.UPDATED)

                                for new_position in new_positions:
                                    old_position = next(
                                        (p for p in positions if p.product == new_position.product),
                                        None
                                    )
                                    # if new position
                                    if not old_position:
                                        positions_callback([new_position], SDKEventType.NEW)

                                positions = new_positions
                        elif isinstance(msg, LogsNotification):
                            if msg.result.value.err is None:
                                events = self.parse_events_from_logs(sdk, msg.result.value.logs)
                                orders = defaultdict(list)
                                fills = []
                                for e in events:
                                    if isinstance(e, OrderPlacedEvent):
                                        product = None
                                        for p in sdk.products:
                                            if p.name == e.product:
                                                product = p
                                                break

                                        orders[SDKEventType.NEW].append(
                                            SDKOrder(
                                                order_id=e.order_id,
                                                product=product,
                                                side=e.side,
                                                price=float(e.price),
                                                qty=float(e.size),
                                                client_order_id=e.client_order_id,
                                                trader_risk_group=self.account,
                                            )
                                        )
                                    elif isinstance(e, OrderCancelledEvent):
                                        product = None
                                        for p in sdk.products:
                                            if p.name == e.product:
                                                product = p
                                                break

                                        price = OrderBook.get_price_from_key(
                                            e.order_id,
                                            product.metadata.tick_size,
                                            product.metadata.price_offset
                                        )

                                        orders[SDKEventType.CANCELLED].append(
                                            SDKOrder(
                                                order_id=e.order_id,
                                                product=product,
                                                side=e.side,
                                                price=float(price),
                                                qty=float(e.size),
                                                client_order_id=e.client_order_id,
                                                trader_risk_group=self.account,
                                            )
                                        )
                                    elif isinstance(e, OrderCompletedEvent):
                                        product = None
                                        for p in sdk.products:
                                            if p.name == e.product:
                                                product = p
                                                break

                                        price = OrderBook.get_price_from_key(
                                            e.order_id,
                                            product.metadata.tick_size,
                                            product.metadata.price_offset
                                        )

                                        if e.reason != CompletedReason.Cancelled:
                                            sdk_event_type = SDKEventType.FILLED if e.reason == CompletedReason.Filled \
                                                else SDKEventType.CANCELLED
                                            orders[sdk_event_type].append(
                                                SDKOrder(
                                                    order_id=e.order_id,
                                                    product=product,
                                                    side=e.side,
                                                    price=float(price),
                                                    qty=float(e.size),
                                                    client_order_id=e.client_order_id,
                                                    trader_risk_group=self.account,
                                                )
                                            )
                                    elif isinstance(e, OrderFillEvent):
                                        product = None
                                        for p in sdk.products:
                                            if p.name == e.product:
                                                product = p
                                                break

                                        fills.append(
                                            SDKFill(
                                                product=product,
                                                maker_order_id=e.maker_order_id,
                                                taker_order_id=e.taker_order_id,
                                                taker_side=e.taker_side,
                                                qty=float(e.base_size),
                                                price=float(e.price),
                                                quote_qty=float(e.quote_size),
                                                maker_trader_risk_group=e.maker_trader_risk_group,
                                                taker_trader_risk_group=e.taker_trader_risk_group,
                                                maker_order_nonce=e.maker_order_nonce,
                                                taker_order_nonce=e.taker_order_nonce,
                                                maker_fee=float(e.maker_fee),
                                                taker_fee=float(e.taker_fee),
                                                is_maker=e.maker_trader_risk_group == self.account,
                                            )
                                        )

                                if orders_callback:
                                    for t, e in orders.items():
                                        if len(e) > 0:
                                            orders_callback(e, t)

                                if fills_callback and len(fills) > 0:
                                    fills_callback(fills, SDKEventType.NEW)

                        else:
                            print(f"Unknown msg: {msg}")
            except Exception as e:
                print(f"Monitoring Exception: {str(e)}")
                continue

    async def subscribe(
        self,
        sdk: "SDKContext",
        ws_url: str,
        positions_callback: Callable[[List[SDKPosition], SDKEventType], Any] = None,
        orders_callback: Callable[[List[SDKOrder], SDKEventType], Any] = None,
        fills_callback: Callable[[SDKFill, SDKEventType], Any] = None,
    ):
        await self._monitor_accounts(sdk, ws_url, positions_callback, orders_callback, fills_callback)

    @staticmethod
    def connect(
            sdk: "SDKContext",
            account: Pubkey,
            keypair: Keypair,
    ) -> "SDKTrader":
        wallet = spl_token_instructions.get_associated_token_address(keypair.pubkey(), sdk.vault_mint)

        trg: dtys.TraderRiskGroup = explore(account).data_obj
        assert trg.market_product_group == sdk.market_product_group
        assert trg.owner == keypair.pubkey()

        whitelist_token_wallet = spl_token_instructions.get_associated_token_address(
            keypair.pubkey(),
            mints.WHITELIST_TOKEN_MINT
        )

        staker_state_key, _ = Pubkey.find_program_address(
            seeds=[
                bytes(keypair.pubkey()),
                bytes(sdk.stake_pool)
            ],
            program_id=sdk.staking_program
        )

        return SDKTrader(
            keypair, account, wallet, trg.fee_state_account, trg.risk_state_account, whitelist_token_wallet,
            staker_state=staker_state_key, _batches_lock=threading.Lock(), _batch_id=0, _pending_batches={})

    def get_trader_risk_group(self) -> Tuple[dtys.TraderRiskGroup, int]:
        account_details = fetch_account_details(self.account)
        return account_details.data_obj, account_details.slot

    def deposit(self, sdk: "SDKContext", qty: Union[float, dtys.Fractional]) -> TraderDepositEvent:
        if not isinstance(qty, dtys.Fractional):
            qty = dtys.Fractional(int(qty * (10 ** sdk.decimals)), sdk.decimals)
        ix = dixs.deposit_funds(
            user=self.keypair.pubkey(),
            user_token_account=self.wallet,
            trader_risk_group=self.account,
            market_product_group=sdk.market_product_group,
            market_product_group_vault=sdk.market_product_group_vault,
            capital_limits=sdk.capital_limits,
            params=dtys.DepositFundsParams(
                quantity=qty,
            ),
            program_id=sdk.dex_program,
        )
        trans_details = sdk.send_instructions(ix)
        if trans_details.error:
            raise ValueError(
                trans_details.error_from_log if trans_details.error_from_log is not None else trans_details.error)
        else:
            events = self.parse_events_from_logs(sdk, trans_details.log_messages)
            for e in events:
                if isinstance(e, TraderDepositEvent):
                    return e
            raise DexEventNotFound("Expected TraderDepositEvent")

    def withdraw(self, sdk: "SDKContext", qty: Union[float, dtys.Fractional]) -> TraderWithdrawalEvent:
        if not isinstance(qty, dtys.Fractional):
            qty = dtys.Fractional(int(qty * 10 ** sdk.decimals), sdk.decimals)

        remaining_accounts = [
            to_account_meta(
                ra,
                is_signer=False,
                is_writable=idx == len(sdk.additional_risk_accts) - 1
            ) for idx, ra in enumerate(sdk.additional_risk_accts)
        ]

        ix = dixs.withdraw_funds(
            user=self.keypair.pubkey(),
            user_token_account=self.wallet,
            trader_risk_group=self.account,
            market_product_group=sdk.market_product_group,
            market_product_group_vault=sdk.market_product_group_vault,
            risk_output_register=sdk.risk_output_register,
            risk_engine_program=sdk.risk_engine_program,
            risk_model_configuration_acct=sdk.risk_model_configuration_acct,
            risk_signer=sdk.risk_signer,
            capital_limits=sdk.capital_limits,
            trader_risk_state_acct=self.trader_risk_state_acct,
            params=dtys.WithdrawFundsParams(
                quantity=qty,
            ),
            program_id=sdk.dex_program,
            remaining_accounts=remaining_accounts,
        )
        trans_details = sdk.send_instructions(ix)
        if trans_details.error:
            raise ValueError(
                trans_details.error_from_log if trans_details.error_from_log is not None else trans_details.error)
        else:
            events = self.parse_events_from_logs(sdk, trans_details.log_messages)
            for e in events:
                if isinstance(e, TraderWithdrawalEvent):
                    return e
            raise DexEventNotFound("Expected TraderWithdrawalEvent")

    def init_batch(self):
        self._batches_lock.acquire()
        batch_id = self._batch_id
        self._batch_id += 1
        self._batches_lock.release()
        self._pending_batches[batch_id] = []
        return batch_id

    def commit_batch(
            self,
            sdk: "SDKContext",
            batch_id: int,
            compute_units: int = 1400000,
            additional_microlamports_per_compute_unit: int = 0,
    ) -> List[DexEvent]:
        if batch_id not in self._pending_batches:
            raise ValueError("Invalid batch_id")

        pending_actions = self._pending_batches.pop(batch_id)
        assert (pending_actions and len(pending_actions) > 0)

        ixs = []
        pending_places = []
        for a in pending_actions:
            if isinstance(a, _PendingNewOrder):
                pending_places.append(a)
                ixs.append(self._place_order_ix(sdk, a.product, a.side, a.size, a.price, a.self_trade_behavior,
                                                a.order_type, sdk.additional_risk_accts, match_limit=a.match_limit,
                                                expiration_slot=a.expiration_slot))
            else:
                ixs.append(a)

        if additional_microlamports_per_compute_unit > 0:
            ixs.insert(0, self._set_compute_unit_price_ix(sdk, additional_microlamports_per_compute_unit))
        ixs.insert(0, self._request_compute_ix(sdk, compute_units))

        trans_details = sdk.send_instructions(*ixs, raise_on_error=False)
        if trans_details.error:
            raise ValueError(
                trans_details.error_from_log if trans_details.error_from_log is not None else trans_details.error)
        else:
            return self.parse_events_from_logs(sdk, trans_details.log_messages)

    def _request_heap_ix(self, sdk: "SDKContext", sz: int = 32 * 1024):
        request_heap = CStruct(
            "bytes" / U32,
        )

        buffer = BytesIO()
        # this is the enum value for SetComputeUnitLimit
        buffer.write(U8.build(1))
        buffer.write(request_heap.build({"bytes": sz}))

        return Instruction(
            accounts=[],
            program_id=Pubkey.from_string("ComputeBudget111111111111111111111111111111"),
            data=buffer.getvalue()
        )

    def _request_compute_ix(self, sdk: "SDKContext", units: int = 1400000):
        request_units = CStruct(
            "units" / U32,
        )

        buffer = BytesIO()
        # this is the enum value for SetComputeUnitLimit
        buffer.write(U8.build(2))
        buffer.write(request_units.build({"units": units}))

        return Instruction(
            accounts=[],
            program_id=Pubkey.from_string("ComputeBudget111111111111111111111111111111"),
            data=buffer.getvalue()
        )

    def _set_compute_unit_price_ix(self, sdk: "SDKContext", microLamports: int = 5000):
        compute_unit_price = CStruct(
            "microLamports" / U64,
        )

        buffer = BytesIO()
        # this is the enum value for SetComputeUnitPrice
        buffer.write(U8.build(3))
        buffer.write(compute_unit_price.build({"microLamports": microLamports}))

        return Instruction(
            accounts=[],
            program_id=Pubkey.from_string("ComputeBudget111111111111111111111111111111"),
            data=buffer.getvalue()
        )

    def place_order(
            self,
            sdk: "SDKContext",
            product: Union[SDKProduct, Pubkey],
            side: aaob_state.Side,
            size: Union[dtys.Fractional, float],
            price: Union[dtys.Fractional, float],
            self_trade_behavior: aaob_state.SelfTradeBehavior = aaob_state.SelfTradeBehavior.CANCEL_PROVIDE,
            order_type: dtys.OrderType = dtys.OrderType.LIMIT,
            batch_id: int = None,
            client_order_id: int = 0,
            match_limit: int = DEFAULT_MATCH_LIMIT,
            expiration_slot: int = 0,
            compute_units: int = 300000,
            additional_microlamports_per_compute_unit: int = 0,
    ) -> Union[OrderPlacedEvent, OrderCompletedEvent]:
        ix = self._place_order_ix(sdk, product, side, size, price, self_trade_behavior, order_type,
                                  sdk.additional_risk_accts, client_order_id=client_order_id, match_limit=match_limit,
                                  expiration_slot=expiration_slot)
        if batch_id is not None:
            self._pending_batches[batch_id].append(
                _PendingNewOrder(product, side, size, price, self_trade_behavior, order_type, match_limit, expiration_slot))
        else:
            ixs = [self._request_compute_ix(sdk, compute_units)]
            if additional_microlamports_per_compute_unit > 0:
                ixs.append(self._set_compute_unit_price_ix(sdk, additional_microlamports_per_compute_unit))
            ixs.append(ix)
            trans_details = sdk.send_instructions(*ixs, raise_on_error=False)
            if trans_details.error:
                raise ValueError(
                    trans_details.error_from_log if trans_details.error_from_log is not None else trans_details.error)
            else:
                events = self.parse_events_from_logs(sdk, trans_details.log_messages)
                for e in events:
                    if isinstance(e, OrderPlacedEvent):
                        return e
                    elif isinstance(e, OrderCompletedEvent):
                        return e
                raise DexEventNotFound("Expected OrderPlacedEvent")

    def _place_order_ix(
            self,
            sdk: "SDKContext",
            product: Union[SDKProduct, Pubkey],
            side: aaob_state.Side,
            size: Union[dtys.Fractional, float],
            price: Union[dtys.Fractional, float],
            self_trade_behavior: aaob_state.SelfTradeBehavior = aaob_state.SelfTradeBehavior.CANCEL_PROVIDE,
            order_type: dtys.OrderType = dtys.OrderType.LIMIT,
            risk_accounts: Optional[List[Pubkey]] = None,
            referrer_trg: Optional[Pubkey] = None,
            referrer_fee_bps: dtys.Fractional = dtys.Fractional(0, 0),
            client_order_id: int = 0,
            match_limit: int = DEFAULT_MATCH_LIMIT,
            expiration_slot: int = 0,
    ):
        remaining_accounts = [
            to_account_meta(
                ra,
                is_signer=False,
                is_writable=idx == len(risk_accounts) - 1
            ) for idx, ra in enumerate(risk_accounts)
        ]
        remaining_accounts.append(to_account_meta(sdk.stake_pool, is_signer=False, is_writable=False))
        remaining_accounts.append(to_account_meta(self.staker_state, is_signer=False, is_writable=False))

        if referrer_trg is None:
            referrer_trg = self.account

        ix = dixs.new_order_v2(
            program_id=sdk.dex_program,
            user=self.keypair.pubkey(),
            trader_risk_group=self.account,
            market_product_group=sdk.market_product_group,
            product=product.key,
            aaob_program=sdk.aaob_program,
            orderbook=product.orderbook,
            market_signer=product.market_signer,
            event_queue=product.event_queue,
            bids=product.bids,
            asks=product.asks,
            fee_model_program=sdk.fee_model_program,
            fee_model_configuration_acct=sdk.fee_model_configuration_acct,
            trader_fee_state_acct=self.trader_fee_state_acct,
            fee_output_register=sdk.fee_output_register,
            risk_engine_program=sdk.risk_engine_program,
            risk_model_configuration_acct=sdk.risk_model_configuration_acct,
            risk_output_register=sdk.risk_output_register,
            trader_risk_state_acct=self.trader_risk_state_acct,
            risk_and_fee_signer=sdk.risk_signer,
            referrer_trg=referrer_trg,
            params=dtys.NewOrderV2Params(
                side=side,
                max_base_qty=dtys.Fractional.into(size, product.metadata.base_decimals),
                order_type=order_type,
                self_trade_behavior=self_trade_behavior,
                match_limit=match_limit,
                limit_price=dtys.Fractional.into(price, 8).simplify(),
                referrer_fee_bps=referrer_fee_bps,
                client_order_id=client_order_id,
                expiration_slot=expiration_slot,
            ),
            remaining_accounts=remaining_accounts,
        )

        return ix

    def multiplace(
            self,
            sdk: "SDKContext",
            product: Union[SDKProduct, Pubkey],
            orders: List[MultiplaceOrder],
            self_trade_behavior: aaob_state.SelfTradeBehavior = aaob_state.SelfTradeBehavior.CANCEL_PROVIDE,
            batch_id: int = None,
            match_limit: int = DEFAULT_MATCH_LIMIT,
            expiration_slot: int = 0,
            compute_units: int = 1400000,
            additional_microlamports_per_compute_unit: int = 0,
            allow_partial_events=False
    ) -> List[Union[OrderPlacedEvent, OrderCompletedEvent]]:
        ix = self._multiplace_ix(sdk, product, orders, self_trade_behavior, sdk.additional_risk_accts,
                                 match_limit=match_limit, expiration_slot=expiration_slot)
        if batch_id is not None:
            self._pending_batches[batch_id].append(ix)
        else:
            ixs = [self._request_compute_ix(sdk, compute_units), self._request_heap_ix(sdk, 256 * 1024)]
            if additional_microlamports_per_compute_unit > 0:
                ixs.append(self._set_compute_unit_price_ix(sdk, additional_microlamports_per_compute_unit))
            ixs.append(ix)
            trans_details = sdk.send_instructions(*ixs, raise_on_error=False)
            if trans_details.error:
                raise ValueError(
                    trans_details.error_from_log if trans_details.error_from_log is not None else trans_details.error)
            else:
                events = self.parse_events_from_logs(sdk, trans_details.log_messages)
                place_events = [e for e in events if isinstance(e, OrderPlacedEvent)
                                or isinstance(e, OrderCompletedEvent)]
                if not allow_partial_events:
                    if len(orders) != len(place_events):
                        raise DexEventNotFound(f"Expected {len(orders)} OrderPlacedEvent, got {len(place_events)}")
                return place_events

    def _multiplace_ix(
            self,
            sdk: "SDKContext",
            product: Union[SDKProduct, Pubkey],
            orders: List[MultiplaceOrder],
            self_trade_behavior: aaob_state.SelfTradeBehavior = aaob_state.SelfTradeBehavior.CANCEL_PROVIDE,
            risk_accounts: Optional[List[Pubkey]] = None,
            referrer_trg: Optional[Pubkey] = None,
            referrer_fee_bps: dtys.Fractional = dtys.Fractional(0, 0),
            match_limit: int = DEFAULT_MATCH_LIMIT,
            expiration_slot: int = 0,
    ):
        remaining_accounts = [
            to_account_meta(
                ra,
                is_signer=False,
                is_writable=idx == len(risk_accounts) - 1
            ) for idx, ra in enumerate(risk_accounts)
        ]
        remaining_accounts.append(to_account_meta(sdk.stake_pool, is_signer=False, is_writable=False))
        remaining_accounts.append(to_account_meta(self.staker_state, is_signer=False, is_writable=False))

        if referrer_trg is None:
            referrer_trg = self.account

        new_order0 = _extract_multiplace_param(orders, 0)
        new_order1 = _extract_multiplace_param(orders, 1)
        new_order2 = _extract_multiplace_param(orders, 2)
        new_order3 = _extract_multiplace_param(orders, 3)
        new_order4 = _extract_multiplace_param(orders, 4)
        new_order5 = _extract_multiplace_param(orders, 5)
        new_order6 = _extract_multiplace_param(orders, 6)
        new_order7 = _extract_multiplace_param(orders, 7)
        new_order8 = _extract_multiplace_param(orders, 8)
        new_order9 = _extract_multiplace_param(orders, 9)
        new_order10 = _extract_multiplace_param(orders, 10)
        new_order11 = _extract_multiplace_param(orders, 11)

        ix = dixs.multiplace_v2(
            program_id=sdk.dex_program,
            user=self.keypair.pubkey(),
            trader_risk_group=self.account,
            market_product_group=sdk.market_product_group,
            product=product.key,
            aaob_program=sdk.aaob_program,
            orderbook=product.orderbook,
            market_signer=product.market_signer,
            event_queue=product.event_queue,
            bids=product.bids,
            asks=product.asks,
            fee_model_program=sdk.fee_model_program,
            fee_model_configuration_acct=sdk.fee_model_configuration_acct,
            trader_fee_state_acct=self.trader_fee_state_acct,
            fee_output_register=sdk.fee_output_register,
            risk_engine_program=sdk.risk_engine_program,
            risk_model_configuration_acct=sdk.risk_model_configuration_acct,
            risk_output_register=sdk.risk_output_register,
            trader_risk_state_acct=self.trader_risk_state_acct,
            risk_and_fee_signer=sdk.risk_signer,
            referrer_trg=referrer_trg,
            params=dtys.MultiplaceV2Params(
                self_trade_behavior=self_trade_behavior,
                match_limit=match_limit,
                referrer_fee_bps=referrer_fee_bps,
                expiration_slot=expiration_slot,
                num_new_orders=len(orders),
                new_order0=new_order0,
                new_order1=new_order1,
                new_order2=new_order2,
                new_order3=new_order3,
                new_order4=new_order4,
                new_order5=new_order5,
                new_order6=new_order6,
                new_order7=new_order7,
                new_order8=new_order8,
                new_order9=new_order9,
                new_order10=new_order10,
                new_order11=new_order11,
            ),
            remaining_accounts=remaining_accounts,
        )

        return ix

    def cancel_all_single_product(
            self,
            sdk: "SDKContext",
            product: SDKProduct,
            batch_id: int = None,
            compute_units: int = 1000000,
            additional_microlamports_per_compute_unit: int = 0,
            update_mark_prices: bool = False,
    ) -> List[OrderCancelledEvent]:
        if batch_id is not None:
            self._pending_batches[batch_id].append(self._cancel_all_ix(sdk, product, self.account))
        else:
            ixs = [self._request_heap_ix(sdk, 256 * 1024)]
            if compute_units != 200000:
                ixs.append(self._request_compute_ix(sdk, compute_units))
            if additional_microlamports_per_compute_unit > 0:
                ixs.append(self._set_compute_unit_price_ix(sdk, additional_microlamports_per_compute_unit))
            if update_mark_prices:
                ixs.append(self._update_mark_prices_ix(sdk, [product]))
            update_variance_cache_ix = self._update_variance_cache_ix(sdk)
            ix = self._cancel_all_ix(sdk, product, self.account)
            trans_details = sdk.send_instructions(*ixs, ix, update_variance_cache_ix, raise_on_error=False)
            if trans_details.error:
                raise ValueError(
                    f"cancel_all: {trans_details.error_from_log if trans_details.error_from_log is not None else trans_details.error}")
            else:
                events = self.parse_events_from_logs(sdk, trans_details.log_messages)
                return [e for e in events if isinstance(e, OrderCancelledEvent)]

    def cancel(
            self,
            sdk: "SDKContext",
            product: SDKProduct,
            order_id: int,
            batch_id: int = None,
            client_order_id: int = 0,
            compute_units: int = 200000,
            additional_microlamports_per_compute_unit: int = 0,
    ) -> OrderCancelledEvent:
        return self.cancel_underwater(sdk, product, order_id, self.account, batch_id=batch_id,
                                      client_order_id=client_order_id,
                                      compute_units=compute_units,
                                      additional_microlamports_per_compute_unit=additional_microlamports_per_compute_unit)

    def cancel_underwater(
            self,
            sdk: "SDKContext",
            product: SDKProduct,
            order_id: int,
            under_water_trg: Pubkey,
            batch_id: int = None,
            no_err: bool = False,
            client_order_id: int = 0,
            compute_units: int = 200000,
            additional_microlamports_per_compute_unit: int = 0,
    ) -> OrderCancelledEvent:
        if batch_id is not None:
            self._pending_batches[batch_id].append(
                self._cancel_ix(sdk, product, order_id, under_water_trg, no_err, client_order_id))
        else:
            ixs = []
            if compute_units != 200000:
                ixs.append(self._request_compute_ix(sdk, compute_units))
            if additional_microlamports_per_compute_unit > 0:
                ixs.append(self._set_compute_unit_price_ix(sdk, additional_microlamports_per_compute_unit))
            update_variance_cache_ix = self._update_variance_cache_ix(sdk)
            ix = self._cancel_ix(sdk, product, order_id, under_water_trg, no_err, client_order_id)
            trans_details = sdk.send_instructions(*ixs, ix, update_variance_cache_ix, raise_on_error=False)
            if trans_details.error:
                raise ValueError(
                    f"{order_id}: {trans_details.error_from_log if trans_details.error_from_log is not None else trans_details.error}")
            else:
                events = self.parse_events_from_logs(sdk, trans_details.log_messages)
                for e in events:
                    if isinstance(e, OrderCancelledEvent):
                        return e
                raise DexEventNotFound("Expected OrderCancelledEvent")

    def _update_variance_cache_ix(
            self,
            sdk: "SDKContext"
    ):
        remaining_accounts = [
            to_account_meta(
                ra,
                is_signer=False,
                is_writable=idx == len(sdk.additional_risk_accts) - 1
            ) for idx, ra in enumerate(sdk.additional_risk_accts)
        ]

        return dixs.update_variance_cache(
            payer=self.keypair.pubkey(),
            trader_risk_group=self.account,
            market_product_group=sdk.market_product_group,
            risk_engine_program=sdk.risk_engine_program,
            risk_model_configuration_acct=sdk.risk_model_configuration_acct,
            risk_output_register=sdk.risk_output_register,
            trader_risk_state_acct=self.trader_risk_state_acct,
            risk_and_fee_signer=sdk.risk_signer,
            remaining_accounts=remaining_accounts
        )

    def update_mark_prices(
            self,
            sdk: "SDKContext"
    ):
        for products in self._chunks(sdk.products, 3):
            sdk.send_instructions(self._update_mark_prices_ix(sdk, products))

    def _update_mark_prices_ix(
            self,
            sdk: "SDKContext",
            products: List["SDKProduct"],
    ):
        return sdk.update_mark_prices_ix(self.keypair, products)

    def _cancel_all_ix(
            self,
            sdk: "SDKContext",
            product: SDKProduct,
            under_water_trg: Pubkey,
    ):
        remaining_accounts = [
            to_account_meta(
                ra,
                is_signer=False,
                is_writable=idx == len(sdk.additional_risk_accts) - 1
            ) for idx, ra in enumerate(sdk.additional_risk_accts)
        ]

        return dixs.cancel_all(
            user=self.keypair.pubkey(),
            trader_risk_group=under_water_trg,
            market_product_group=sdk.market_product_group,
            product=product.key,
            aaob_program=sdk.aaob_program,
            orderbook=product.orderbook,
            market_signer=product.market_signer,
            event_queue=product.event_queue,
            bids=product.bids,
            asks=product.asks,
            risk_engine_program=sdk.risk_engine_program,
            risk_model_configuration_acct=sdk.risk_model_configuration_acct,
            risk_output_register=sdk.risk_output_register,
            trader_risk_state_acct=self.trader_risk_state_acct,
            risk_signer=sdk.risk_signer,
            remaining_accounts=remaining_accounts,
            program_id=sdk.dex_program,
        )

    def _cancel_ix(
            self,
            sdk: "SDKContext",
            product: SDKProduct,
            order_id: int,
            under_water_trg: Pubkey,
            no_err: bool,
            client_order_id: int,
    ):
        remaining_accounts = [
            to_account_meta(
                ra,
                is_signer=False,
                is_writable=idx == len(sdk.additional_risk_accts) - 1
            ) for idx, ra in enumerate(sdk.additional_risk_accts)
        ]

        return dixs.cancel_order(
            user=self.keypair.pubkey(),
            trader_risk_group=under_water_trg,
            market_product_group=sdk.market_product_group,
            product=product.key,
            aaob_program=sdk.aaob_program,
            orderbook=product.orderbook,
            market_signer=product.market_signer,
            event_queue=product.event_queue,
            bids=product.bids,
            asks=product.asks,
            risk_engine_program=sdk.risk_engine_program,
            risk_model_configuration_acct=sdk.risk_model_configuration_acct,
            risk_output_register=sdk.risk_output_register,
            trader_risk_state_acct=self.trader_risk_state_acct,
            risk_signer=sdk.risk_signer,
            params=CancelOrderParams(order_id=order_id, no_err=[1] if no_err else [0], client_order_id=client_order_id),
            remaining_accounts=remaining_accounts,
            program_id=sdk.dex_program,
        )

        # workaround to correctly serialize no_err

    #        ix_data = bytearray(ix.data)
    #        if len(ix_data) < 25:
    #            ix_data.append(0)
    #        if no_err:
    #            ix_data = ix_data[:-1] + b'\x01'

    def replace(
            self,
            sdk: "SDKContext",
            product: Union[SDKProduct, Pubkey],
            order_id: int,
            side: aaob_state.Side,
            size: Union[dtys.Fractional, float],
            price: Union[dtys.Fractional, float],
            self_trade_behavior: aaob_state.SelfTradeBehavior = aaob_state.SelfTradeBehavior.CANCEL_PROVIDE,
            order_type: dtys.OrderType = dtys.OrderType.LIMIT,
            batch_id: int = None,
            cancel_no_err: bool = True,
            client_order_id: int = 0,
            match_limit: int = DEFAULT_MATCH_LIMIT,
            expiration_slot: int = 0,
            compute_units: int = 400000,
            additional_microlamports_per_compute_unit: int = 0,
    ) -> OrderPlacedEvent:
        cancel_ix = self._cancel_ix(sdk, product, order_id, self.account, no_err=cancel_no_err,
                                    client_order_id=client_order_id)
        place_ix = self._place_order_ix(sdk, product, side, size, price, self_trade_behavior, order_type,
                                        sdk.additional_risk_accts, client_order_id=client_order_id,
                                        match_limit=match_limit, expiration_slot=expiration_slot)

        if batch_id is not None:
            self._pending_batches[batch_id].append(cancel_ix)
            self._pending_batches[batch_id].append(
                _PendingNewOrder(product, side, size, price, self_trade_behavior, order_type, match_limit, expiration_slot))
        else:
            ixs = [self._request_compute_ix(sdk, compute_units)]
            if additional_microlamports_per_compute_unit > 0:
                ixs.append(self._set_compute_unit_price_ix(sdk, additional_microlamports_per_compute_unit))
            trans_details = sdk.send_instructions(*ixs, cancel_ix, place_ix, raise_on_error=False)
            if trans_details.error:
                raise Exception(
                    trans_details.error_from_log if trans_details.error_from_log is not None else trans_details.error)
            else:
                events = self.parse_events_from_logs(sdk, trans_details.log_messages)
                for e in events:
                    if isinstance(e, OrderPlacedEvent):
                        return e
                raise DexEventNotFound("Expected OrderPlacedEvent")

    def open_positions(
            self,
            sdk: "SDKContext",
            trg: dtys.TraderRiskGroup = None
    ) -> Iterable[SDKPosition]:
        if not trg:
            trg, _ = self.get_trader_risk_group()
        for position in trg.trader_positions:
            if position.tag == account_tag.AccountTag.UNINITIALIZED or \
                    (position.position.value == 0 and position.pending_position.value == 0):
                continue
            yield SDKPosition(
                next(product for product in sdk.products if product.key == position.product_key),
                position.position.value,
                position.pending_position.value,
                position.last_cum_funding_snapshot.value,
                position.last_social_loss_snapshot.value
            )

    def open_orders(
            self,
            sdk: "SDKContext",
            products: List[SDKProduct] = None,
            trg: dtys.TraderRiskGroup = None
    ) -> Iterable[SDKOrder]:
        if products is None or len(products) == 0:
            products = sdk.products

        if not trg:
            trg, slot = self.get_trader_risk_group()
        for p in products:
            ptr = trg.open_orders.products[p.index].head_index
            order = trg.open_orders.orders[ptr]
            assert order.prev == SENTINEL
            while ptr != SENTINEL:
                order = trg.open_orders.orders[ptr]
                assert order.id != 0
                yield SDKOrder(
                    order.id,
                    p,
                    aaob_state.Side.BID if OrderBook.key_is_bid(order.id) else aaob_state.Side.ASK,
                    OrderBook.get_price_from_key(order.id, p.metadata.tick_size, p.metadata.price_offset),
                    order.qty / (10 ** p.metadata.base_decimals),
                    order.client_id,
                    self.account,
                )
                ptr = order.next

    def open_order_ids(
            self,
            sdk: "SDKContext",
            products: List[SDKProduct] = None,
            trg: dtys.TraderRiskGroup = None
    ) -> Iterable[SDKProduct, int]:
        if products is None or len(products) == 0:
            products = sdk.products

        if not trg:
            trg, _ = self.get_trader_risk_group()
        for p in products:
            ptr = trg.open_orders.products[p.index].head_index
            order = trg.open_orders.orders[ptr]
            assert order.prev == SENTINEL
            while ptr != SENTINEL:
                order = trg.open_orders.orders[ptr]
                assert order.id != 0
                yield p, order.id
                ptr = order.next

    def _chunks(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    def parse_events_from_logs(self, sdk: "SDKContext", logs: List[str], allow_all_mpgs=False):
        events = sdk.parse_events_from_logs(logs)
        trader_events = []
        for e in events:
            if not allow_all_mpgs and sdk.market_product_group != e.market_product_group:
                continue
            if isinstance(e, OrderPlacedEvent):
                if e.trader_risk_group == self.account:
                    trader_events.append(e)
            elif isinstance(e, OrderFillEvent):
                if e.maker_trader_risk_group == self.account or e.taker_trader_risk_group == self.account:
                    trader_events.append(e)
            elif isinstance(e, OrderCancelledEvent):
                if e.trader_risk_group == self.account:
                    trader_events.append(e)
            elif isinstance(e, OrderCompletedEvent):
                if e.trader_risk_group == self.account:
                    trader_events.append(e)
            elif isinstance(e, TraderDepositEvent):
                if e.trader_risk_group == self.account:
                    trader_events.append(e)
            elif isinstance(e, TraderWithdrawalEvent):
                if e.trader_risk_group == self.account:
                    trader_events.append(e)
            elif isinstance(e, TraderLiquidationEvent):
                if e.liquidator_trader_risk_group == self.account or e.liquidatee_trader_risk_group == self.account:
                    trader_events.append(e)
            elif isinstance(e, TraderApplyFundingEvent):
                if e.trader_risk_group == self.account:
                    trader_events.append(e)
        return trader_events

    def cancel_all_orders(
            self,
            sdk: "SDKContext",
            products: List[SDKProduct] = None,
            compute_units: int = 1000000,
            additional_microlamports_per_compute_unit: int = 0,
            update_mark_prices: bool = False,
    ):
        if products is None or len(products) == 0:
            products = sdk.products

        for p in products:
            self.cancel_all_single_product(sdk, p, compute_units=compute_units,
                                           additional_microlamports_per_compute_unit=additional_microlamports_per_compute_unit,
                                           update_mark_prices=update_mark_prices)


@dataclass
class SDKContext:
    # event parsing
    event_parser: EventParser
    # mpg stuff
    product_group_name: str  # max 16 chars
    trader_risk_state_account_len: int
    decimals: int
    # cached products, reload if necessary
    products: List[SDKProduct]
    # program_ids
    dex_program: Pubkey
    aaob_program: Pubkey
    risk_engine_program: Pubkey
    instruments_program: Pubkey
    # dummy_oracle_program_id: Pubkey
    fee_model_program: Pubkey
    staking_program: Pubkey
    # accts
    market_product_group: Pubkey
    capital_limits: Pubkey
    payer: Keypair
    market_product_group_vault: Pubkey
    vault_mint: Pubkey
    fee_model_configuration_acct: Pubkey
    risk_model_configuration_acct: Pubkey
    risk_signer: Pubkey
    fee_signer: Pubkey
    risk_output_register: Pubkey
    fee_output_register: Pubkey
    fee_collector: Pubkey
    stake_pool: Pubkey
    additional_risk_accts: List[Pubkey]
    address_lookup_table_account: Optional[AddressLookupTableAccount]

    @staticmethod
    def connect(client: Client,
                payer: Keypair,
                market_product_group_key: Pubkey,
                trader_risk_state_account_len: int = 0,
                dex_program_id: Pubkey = pids.DEX_PROGRAM_ID,
                aaob_program_id: Pubkey = pids.AOB_PROGRAM_ID,
                risk_engine_program_id: Pubkey = pids.RISK_ENGINE_PROGRAM_ID,
                instruments_program_id: Pubkey = pids.INSTRUMENTS_PROGRAM_ID,
                staking_program_id: Pubkey = pids.STAKING_PROGRAM_ID,
                stake_pool: Pubkey = Pubkey.from_string("9zdpqAgENj4734TQvqjczMg2ekvvuGsxwJC6f7F1QWp4"),
                raise_on_error: bool = False,
                **kwargs):
        parser = AccountParser()
        parser.register_parser_from_account_enum(pids.DEX_PROGRAM_ID, DexAccounts)
        parser.register_parser_from_account_enum(pids.RISK_ENGINE_PROGRAM_ID, RiskEngineAccounts)
        parser.register_parser(pids.AOB_PROGRAM_ID, aaob_state.account_parser)
        parser.register_parser_from_account_enum(pids.INSTRUMENTS_PROGRAM_ID, InstrumentAccounts)
        Context.init_globals(
            fee_payer=payer,
            client=client,
            signers=[(payer, "payer")],
            parser=parser,
            raise_on_error=raise_on_error,
        )

        mpg: MarketProductGroup = solana_utils.explore(market_product_group_key).data_obj

        address_lookup_table_account = None
        try:
            address_lookup_table_account = solana_utils.get_address_lookup_table_account(mpg.address_lookup_table)
        except:
            pass

        capital_limits_key, _ = Pubkey.find_program_address(
            [b"capital_limits_state", bytes(market_product_group_key)],
            dex_program_id
        )

        s_account, _ = Pubkey.find_program_address(
            [b"s", bytes(market_product_group_key)],
            risk_engine_program_id
        )

        r_account, _ = Pubkey.find_program_address(
            [b"r", bytes(market_product_group_key)],
            risk_engine_program_id
        )

        mark_prices_account, _ = Pubkey.find_program_address(
            [b"mark_prices", bytes(market_product_group_key)],
            risk_engine_program_id
        )

        system_program_id = Pubkey.from_string("11111111111111111111111111111111")

        hxro_multisig = Pubkey.from_string("Fsc6fnvUAKyodgfSmwL6YbvUiZq86nF6bQ5ybb57Ytd7")

        program = Program(idl, dex_program_id, provider=Provider.readonly())
        event_parser = EventParser(dex_program_id, program.coder)

        sdk_context = SDKContext(
            event_parser=event_parser,
            product_group_name=bytes(mpg.name).decode("utf-8").strip(),
            trader_risk_state_account_len=trader_risk_state_account_len,
            decimals=mpg.decimals,
            # cached products reload if necessary
            products=[],
            # program_ids
            dex_program=dex_program_id,
            aaob_program=aaob_program_id,
            risk_engine_program=risk_engine_program_id,
            instruments_program=instruments_program_id,
            # dummy_oracle_program_id=None,
            fee_model_program=mpg.fee_model_program_id,
            staking_program=staking_program_id,
            # accts
            market_product_group=market_product_group_key,
            capital_limits=capital_limits_key,
            payer=payer,
            market_product_group_vault=daddrs.get_market_product_group_vault(market_product_group_key),
            vault_mint=mpg.vault_mint,
            fee_model_configuration_acct=mpg.fee_model_configuration_acct,
            risk_model_configuration_acct=mpg.risk_model_configuration_acct,
            risk_signer=daddrs.get_risk_signer(market_product_group_key),
            fee_signer=daddrs.get_risk_signer(market_product_group_key),
            risk_output_register=mpg.risk_output_register,
            fee_output_register=mpg.fee_output_register,
            fee_collector=mpg.fee_collector,
            stake_pool=stake_pool,
            additional_risk_accts=[s_account, r_account, mark_prices_account, system_program_id, hxro_multisig],
            address_lookup_table_account=address_lookup_table_account,
        )
        sdk_context.load_products()
        return sdk_context

    def list_trader_risk_groups(self) -> List[Pubkey]:
        account_discriminator_filter = types.MemcmpOpts(
            offset=0,
            bytes=str(base58.b58encode(
                int(DexAccounts.TRADER_RISK_GROUP).to_bytes(8, "little")
            ), 'utf-8')
        )
        mpg_filter = types.MemcmpOpts(
            offset=16,
            bytes=str(base58.b58encode(bytes(self.market_product_group)), 'utf-8')
        )
        trader_filter = types.MemcmpOpts(
            offset=48,
            bytes=str(base58.b58encode(bytes(self.payer.pubkey())), 'utf-8')
        )
        response = Context.get_global_client().get_program_accounts(
            pubkey=self.dex_program,
            commitment=Confirmed,
            encoding="base64",
            data_slice=types.DataSliceOpts(offset=0, length=0),  # we don't need any data
            filters=[account_discriminator_filter, mpg_filter, trader_filter]
        )
        trgs = []
        for account in response.value:
            trgs.append(account.pubkey)
        return trgs

    def load_mpg(self) -> MarketProductGroup:
        return fetch_account_details(self.market_product_group).data_obj

    def load_mark_prices(self) -> MarkPricesArray:
        return fetch_account_details(self.additional_risk_accts[2]).data_obj

    def get_mark_price(self, product_key: Pubkey) -> dtys.Fractional:
        return self.extract_mark_price(self.load_mark_prices(), product_key)

    def extract_mark_price(self, mark_prices_array: MarkPricesArray, product_key: Pubkey) -> dtys.Fractional:
        for mp in mark_prices_array.array:
            if mp.product_key == product_key:
                return dtys.Fractional(mp.mark_price.value, 6)
        raise ValueError(f"extract_mark_price failed because no such product found on mark prices array: {product_key}")

    def get_oracle_minus_book_ewma(self, product_key: Pubkey) -> dtys.Fractional:
        return self.extract_oracle_minus_book_ewma(self.load_mark_prices(), product_key)

    def extract_oracle_minus_book_ewma(self, mark_prices_array: MarkPricesArray,
                                       product_key: Pubkey) -> dtys.Fractional:
        for mp in mark_prices_array.array:
            if mp.product_key == product_key:
                return dtys.Fractional(mp.oracle_minus_book_ewma.value, 6)
        raise ValueError(
            f"extract_oracle_minus_book_ewma failed because no such product found on mark prices array: {product_key}")

    def get_index_price(self, product_key: Pubkey) -> dtys.Fractional:
        return self.extract_index_price(self.load_mark_prices(), product_key)

    def extract_index_price(self, mark_prices_array: MarkPricesArray, product_key: Pubkey) -> dtys.Fractional:
        mark_price = self.extract_mark_price(mark_prices_array, product_key)
        ema = self.extract_oracle_minus_book_ewma(mark_prices_array, product_key)
        return mark_price + ema

    def parse_events_from_logs(self, logs: List[str]):
        parsed = []
        events = []
        processed_logs = []
        for log_line in logs:
            if log_line.startswith("Program log: "):
                if log_line.startswith("Program log: lz4:"):
                    lz4_b64 = log_line[17:]
                    if len(lz4_b64) > 0:
                        lz4_bytes = base64.b64decode(lz4_b64)
                        decompressed_str = lz4.block.decompress(lz4_bytes, uncompressed_size=50000).decode("utf-8")
                        b64_events = decompressed_str.split(",")
                        for e in b64_events:
                            processed_logs.append("Program data: " + e)
            else:
                processed_logs.append(log_line)
        self.event_parser.parse_logs(processed_logs, lambda e: parsed.append(e))
        for event in parsed:
            if event.name.startswith(OrderPlacedEvent.__name__):
                events.append(OrderPlacedEvent.from_event(event))
            elif event.name.startswith(OrderFillEvent.__name__):
                events.append(OrderFillEvent.from_event(event))
            elif event.name.startswith(OrderCompletedEvent.__name__):
                events.append(OrderCompletedEvent.from_event(event))
            elif event.name.startswith(OrderCancelledEvent.__name__):
                events.append(OrderCancelledEvent.from_event(event))
            elif event.name.startswith(TraderLiquidationEvent.__name__):
                events.append(TraderLiquidationEvent.from_event(event))
            elif event.name.startswith(TraderDepositEvent.__name__):
                events.append(TraderDepositEvent.from_event(event))
            elif event.name.startswith(TraderWithdrawalEvent.__name__):
                events.append(TraderWithdrawalEvent.from_event(event))
            elif event.name.startswith(TraderApplyFundingEvent.__name__):
                events.append(TraderApplyFundingEvent.from_event(event))
            else:
                pass
        return events

    def load_products(self):
        mpg = self.load_mpg()
        products = []

        mark_prices: MarkPricesArray = fetch_account_details(self.additional_risk_accts[2]).data_obj

        for idx, prod in mpg.active_products():
            if mpg.is_expired(prod):
                continue
            metadata = prod.metadata()
            product_name = bytes(metadata.name).decode('utf-8').strip()
            try:
                orderbook: aaob_state.MarketState = fetch_account_details(metadata.orderbook).data_obj

                price_oracle = None
                if mark_prices.is_hardcoded_oracle:
                    price_oracle = mark_prices.hardcoded_oracle
                elif not mark_prices.is_hardcoded_oracle and prod.is_outright():
                    derivative_metadata: DerivativeMetadata = fetch_account_details(metadata.product_key).data_obj
                    price_oracle = derivative_metadata.price_oracle

                products.append(
                    SDKProduct(
                        metadata.product_key,
                        idx,
                        product_name,
                        orderbook=metadata.orderbook,
                        asks=orderbook.asks,
                        bids=orderbook.bids,
                        event_queue=orderbook.event_queue,
                        market_signer=daddrs.get_market_signer(metadata.product_key),
                        metadata=metadata,
                        price_oracle=price_oracle,
                        is_combo=prod.is_combo(),
                    )
                )
            except:
                print(f"WARNING: Ignoring invalid product {product_name}")
                continue

        self.products = products

    def product_from_name(self, product_name) -> SDKProduct:
        name = bytes(product_name).decode('utf-8').strip()
        for p in self.products:
            if p.name == name:
                return p
        return None

    def send_instructions(self, *ixs: Instruction, **kwargs):
        return solana_utils.send_instructions(*ixs, **kwargs, address_lookup_table_accounts=[
            self.address_lookup_table_account] if self.address_lookup_table_account else None)

    def register_trader(self, keypair: Keypair):
        trader_risk_group = Keypair()
        trader_risk_state_acct = Keypair()
        _ident = str(keypair.pubkey())[:8]
        Context.add_signers(
            (trader_risk_state_acct, f"{_ident}'s {Context.trader_nonce}-th trader_risk_state_acct"),
            (trader_risk_group, f"{_ident}'s {Context.trader_nonce}-th trader_risk_group)"),
        )
        Context.trader_nonce += 1
        trader_fee_state_acct = daddrs.get_trader_fee_state_acct(
            trader_risk_group.pubkey(),
            self.market_product_group,
            self.fee_model_configuration_acct,
            self.fee_model_program
        )

        size = 13288
        allocate_trg = system_program.create_account(
            system_program.CreateAccountParams(
                from_pubkey=self.payer.pubkey(),
                to_pubkey=trader_risk_group.pubkey(),
                lamports=solana_utils.calc_rent(size),
                space=size,
                owner=self.dex_program,
            )
        )
        trg_init_ix = dixs.initialize_trader_risk_group(
            owner=keypair.pubkey(),
            trader_risk_group=trader_risk_group.pubkey(),
            trader_risk_state_acct=trader_risk_state_acct.pubkey(),
            trader_fee_state_acct=trader_fee_state_acct,
            market_product_group=self.market_product_group,
            risk_signer=self.risk_signer,
            risk_engine_program=self.risk_engine_program,
            fee_model_config_acct=self.fee_model_configuration_acct,
            fee_model_program=self.fee_model_program,
            program_id=self.dex_program,
            # **vars(self),
        )
        self.send_instructions(allocate_trg, trg_init_ix)
        return SDKTrader.connect(
            self,
            trader_risk_group.pubkey(),
            keypair,
        )

    def update_mark_prices_ix(
            self,
            payer: Keypair,
            products: List["SDKProduct"],
    ):
        remaining_accounts = []

        num_products = 0

        for product in products:
            if product.is_combo:
                continue
            for acc in [product.key, product.price_oracle, product.orderbook, product.bids, product.asks]:
                remaining_accounts.append(to_account_meta(acc, is_signer=False, is_writable=False))
            num_products = num_products + 1

        ix = rixs.update_mark_prices(
            payer=payer.pubkey(),
            mark_prices=self.additional_risk_accts[2],
            market_product_group=self.market_product_group,
            remaining_accounts=remaining_accounts,
            params=UpdateMarkPricesParams(num_products=num_products),
        )

        return ix
