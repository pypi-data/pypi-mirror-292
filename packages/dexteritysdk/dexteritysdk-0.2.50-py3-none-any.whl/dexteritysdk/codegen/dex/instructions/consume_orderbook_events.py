# LOCK-BEGIN[imports]: DON'T MODIFY
from .instruction_tag import InstructionTag
from dataclasses import dataclass
from dexteritysdk.codegen.dex.types import ConsumeOrderbookEventsParams
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


# LOCK-BEGIN[ix_cls(consume_orderbook_events)]: DON'T MODIFY
@dataclass
class ConsumeOrderbookEventsIx:
    program_id: Pubkey

    # account metas
    aaob_program: AccountMeta
    market_product_group: AccountMeta
    product: AccountMeta
    market_signer: AccountMeta
    orderbook: AccountMeta
    event_queue: AccountMeta
    reward_target: AccountMeta
    fee_model_program: AccountMeta
    fee_model_configuration_acct: AccountMeta
    fee_output_register: AccountMeta
    risk_and_fee_signer: AccountMeta
    remaining_accounts: Optional[List[AccountMeta]]

    # data fields
    params: ConsumeOrderbookEventsParams

    def to_instruction(self):
        keys = []
        keys.append(self.aaob_program)
        keys.append(self.market_product_group)
        keys.append(self.product)
        keys.append(self.market_signer)
        keys.append(self.orderbook)
        keys.append(self.event_queue)
        keys.append(self.reward_target)
        keys.append(self.fee_model_program)
        keys.append(self.fee_model_configuration_acct)
        keys.append(self.fee_output_register)
        keys.append(self.risk_and_fee_signer)
        if self.remaining_accounts is not None:
            keys.extend(self.remaining_accounts)

        buffer = BytesIO()
        buffer.write(InstructionTag.to_bytes(InstructionTag.CONSUME_ORDERBOOK_EVENTS))
        buffer.write(BYTES_CATALOG.pack(ConsumeOrderbookEventsParams, self.params))

        return Instruction(
            accounts=keys,
            program_id=self.program_id,
            data=buffer.getvalue(),
        )

# LOCK-END


# LOCK-BEGIN[ix_fn(consume_orderbook_events)]: DON'T MODIFY
def consume_orderbook_events(
    aaob_program: Union[str, Pubkey, AccountMeta],
    market_product_group: Union[str, Pubkey, AccountMeta],
    product: Union[str, Pubkey, AccountMeta],
    market_signer: Union[str, Pubkey, AccountMeta],
    orderbook: Union[str, Pubkey, AccountMeta],
    event_queue: Union[str, Pubkey, AccountMeta],
    reward_target: Union[str, Pubkey, AccountMeta],
    fee_model_program: Union[str, Pubkey, AccountMeta],
    fee_model_configuration_acct: Union[str, Pubkey, AccountMeta],
    fee_output_register: Union[str, Pubkey, AccountMeta],
    risk_and_fee_signer: Union[str, Pubkey, AccountMeta],
    params: ConsumeOrderbookEventsParams,
    remaining_accounts: Optional[List[AccountMeta]] = None,
    program_id: Optional[Pubkey] = None,
):
    if program_id is None:
        program_id = Pubkey.from_string("FUfpR31LmcP1VSbz5zDaM7nxnH55iBHkpwusgrnhaFjL")

    if isinstance(aaob_program, (str, Pubkey)):
        aaob_program = to_account_meta(
            aaob_program,
            is_signer=False,
            is_writable=False,
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
    if isinstance(market_signer, (str, Pubkey)):
        market_signer = to_account_meta(
            market_signer,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(orderbook, (str, Pubkey)):
        orderbook = to_account_meta(
            orderbook,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(event_queue, (str, Pubkey)):
        event_queue = to_account_meta(
            event_queue,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(reward_target, (str, Pubkey)):
        reward_target = to_account_meta(
            reward_target,
            is_signer=True,
            is_writable=True,
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
    if isinstance(fee_output_register, (str, Pubkey)):
        fee_output_register = to_account_meta(
            fee_output_register,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(risk_and_fee_signer, (str, Pubkey)):
        risk_and_fee_signer = to_account_meta(
            risk_and_fee_signer,
            is_signer=False,
            is_writable=False,
        )

    return ConsumeOrderbookEventsIx(
        program_id=program_id,
        aaob_program=aaob_program,
        market_product_group=market_product_group,
        product=product,
        market_signer=market_signer,
        orderbook=orderbook,
        event_queue=event_queue,
        reward_target=reward_target,
        fee_model_program=fee_model_program,
        fee_model_configuration_acct=fee_model_configuration_acct,
        fee_output_register=fee_output_register,
        risk_and_fee_signer=risk_and_fee_signer,
        remaining_accounts=remaining_accounts,
        params=params,
    ).to_instruction()

# LOCK-END
