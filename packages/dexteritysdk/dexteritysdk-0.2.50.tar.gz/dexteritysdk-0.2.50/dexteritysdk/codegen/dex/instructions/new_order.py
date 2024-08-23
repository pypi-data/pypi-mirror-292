# LOCK-BEGIN[imports]: DON'T MODIFY
from .instruction_tag import InstructionTag
from dataclasses import dataclass
from dexteritysdk.codegen.dex.types import NewOrderParams
from dexteritysdk.solmate.utils import to_account_meta
from io import BytesIO
from podite import BYTES_CATALOG
from solders.instruction import (
    AccountMeta,
    Instruction,
)
from solders.pubkey import Pubkey
from typing import (
    List,
    Optional,
    Union,
)

# LOCK-END


# LOCK-BEGIN[ix_cls(new_order)]: DON'T MODIFY
@dataclass
class NewOrderIx:
    program_id: Pubkey

    # account metas
    user: AccountMeta
    trader_risk_group: AccountMeta
    market_product_group: AccountMeta
    product: AccountMeta
    aaob_program: AccountMeta
    orderbook: AccountMeta
    market_signer: AccountMeta
    event_queue: AccountMeta
    bids: AccountMeta
    asks: AccountMeta
    system_program: AccountMeta
    fee_model_program: AccountMeta
    fee_model_configuration_acct: AccountMeta
    trader_fee_state_acct: AccountMeta
    fee_output_register: AccountMeta
    risk_engine_program: AccountMeta
    risk_model_configuration_acct: AccountMeta
    risk_output_register: AccountMeta
    trader_risk_state_acct: AccountMeta
    risk_and_fee_signer: AccountMeta
    referrer_trg: AccountMeta
    remaining_accounts: Optional[List[AccountMeta]]

    # data fields
    params: NewOrderParams

    def to_instruction(self):
        keys = []
        keys.append(self.user)
        keys.append(self.trader_risk_group)
        keys.append(self.market_product_group)
        keys.append(self.product)
        keys.append(self.aaob_program)
        keys.append(self.orderbook)
        keys.append(self.market_signer)
        keys.append(self.event_queue)
        keys.append(self.bids)
        keys.append(self.asks)
        keys.append(self.system_program)
        keys.append(self.fee_model_program)
        keys.append(self.fee_model_configuration_acct)
        keys.append(self.trader_fee_state_acct)
        keys.append(self.fee_output_register)
        keys.append(self.risk_engine_program)
        keys.append(self.risk_model_configuration_acct)
        keys.append(self.risk_output_register)
        keys.append(self.trader_risk_state_acct)
        keys.append(self.risk_and_fee_signer)
        keys.append(self.referrer_trg)
        if self.remaining_accounts is not None:
            keys.extend(self.remaining_accounts)

        buffer = BytesIO()
        buffer.write(InstructionTag.to_bytes(InstructionTag.NEW_ORDER))
        buffer.write(BYTES_CATALOG.pack(NewOrderParams, self.params))

        return Instruction(
            accounts=keys,
            program_id=self.program_id,
            data=buffer.getvalue(),
        )

# LOCK-END


# LOCK-BEGIN[ix_fn(new_order)]: DON'T MODIFY
def new_order(
    user: Union[str, Pubkey, AccountMeta],
    trader_risk_group: Union[str, Pubkey, AccountMeta],
    market_product_group: Union[str, Pubkey, AccountMeta],
    product: Union[str, Pubkey, AccountMeta],
    aaob_program: Union[str, Pubkey, AccountMeta],
    orderbook: Union[str, Pubkey, AccountMeta],
    market_signer: Union[str, Pubkey, AccountMeta],
    event_queue: Union[str, Pubkey, AccountMeta],
    bids: Union[str, Pubkey, AccountMeta],
    asks: Union[str, Pubkey, AccountMeta],
    fee_model_program: Union[str, Pubkey, AccountMeta],
    fee_model_configuration_acct: Union[str, Pubkey, AccountMeta],
    trader_fee_state_acct: Union[str, Pubkey, AccountMeta],
    fee_output_register: Union[str, Pubkey, AccountMeta],
    risk_engine_program: Union[str, Pubkey, AccountMeta],
    risk_model_configuration_acct: Union[str, Pubkey, AccountMeta],
    risk_output_register: Union[str, Pubkey, AccountMeta],
    trader_risk_state_acct: Union[str, Pubkey, AccountMeta],
    risk_and_fee_signer: Union[str, Pubkey, AccountMeta],
    referrer_trg: Union[str, Pubkey, AccountMeta],
    params: NewOrderParams,
    system_program: Union[str, Pubkey, AccountMeta] = Pubkey.from_string("11111111111111111111111111111111"),
    remaining_accounts: Optional[List[AccountMeta]] = None,
    program_id: Optional[Pubkey] = None,
):
    if program_id is None:
        program_id = Pubkey.from_string("FUfpR31LmcP1VSbz5zDaM7nxnH55iBHkpwusgrnhaFjL")

    if isinstance(user, (str, Pubkey)):
        user = to_account_meta(
            user,
            is_signer=True,
            is_writable=True,
        )
    if isinstance(trader_risk_group, (str, Pubkey)):
        trader_risk_group = to_account_meta(
            trader_risk_group,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(market_product_group, (str, Pubkey)):
        market_product_group = to_account_meta(
            market_product_group,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(product, (str, Pubkey)):
        product = to_account_meta(
            product,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(aaob_program, (str, Pubkey)):
        aaob_program = to_account_meta(
            aaob_program,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(orderbook, (str, Pubkey)):
        orderbook = to_account_meta(
            orderbook,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(market_signer, (str, Pubkey)):
        market_signer = to_account_meta(
            market_signer,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(event_queue, (str, Pubkey)):
        event_queue = to_account_meta(
            event_queue,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(bids, (str, Pubkey)):
        bids = to_account_meta(
            bids,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(asks, (str, Pubkey)):
        asks = to_account_meta(
            asks,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(system_program, (str, Pubkey)):
        system_program = to_account_meta(
            system_program,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(fee_model_program, (str, Pubkey)):
        fee_model_program = to_account_meta(
            fee_model_program,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(fee_model_configuration_acct, (str, Pubkey)):
        fee_model_configuration_acct = to_account_meta(
            fee_model_configuration_acct,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(trader_fee_state_acct, (str, Pubkey)):
        trader_fee_state_acct = to_account_meta(
            trader_fee_state_acct,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(fee_output_register, (str, Pubkey)):
        fee_output_register = to_account_meta(
            fee_output_register,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(risk_engine_program, (str, Pubkey)):
        risk_engine_program = to_account_meta(
            risk_engine_program,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(risk_model_configuration_acct, (str, Pubkey)):
        risk_model_configuration_acct = to_account_meta(
            risk_model_configuration_acct,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(risk_output_register, (str, Pubkey)):
        risk_output_register = to_account_meta(
            risk_output_register,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(trader_risk_state_acct, (str, Pubkey)):
        trader_risk_state_acct = to_account_meta(
            trader_risk_state_acct,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(risk_and_fee_signer, (str, Pubkey)):
        risk_and_fee_signer = to_account_meta(
            risk_and_fee_signer,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(referrer_trg, (str, Pubkey)):
        referrer_trg = to_account_meta(
            referrer_trg,
            is_signer=False,
            is_writable=True,
        )

    return NewOrderIx(
        program_id=program_id,
        user=user,
        trader_risk_group=trader_risk_group,
        market_product_group=market_product_group,
        product=product,
        aaob_program=aaob_program,
        orderbook=orderbook,
        market_signer=market_signer,
        event_queue=event_queue,
        bids=bids,
        asks=asks,
        system_program=system_program,
        fee_model_program=fee_model_program,
        fee_model_configuration_acct=fee_model_configuration_acct,
        trader_fee_state_acct=trader_fee_state_acct,
        fee_output_register=fee_output_register,
        risk_engine_program=risk_engine_program,
        risk_model_configuration_acct=risk_model_configuration_acct,
        risk_output_register=risk_output_register,
        trader_risk_state_acct=trader_risk_state_acct,
        risk_and_fee_signer=risk_and_fee_signer,
        referrer_trg=referrer_trg,
        remaining_accounts=remaining_accounts,
        params=params,
    ).to_instruction()

# LOCK-END
