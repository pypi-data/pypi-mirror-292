# LOCK-BEGIN[imports]: DON'T MODIFY
from .instruction_tag import InstructionTag
from dataclasses import dataclass
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


# LOCK-BEGIN[ix_cls(update_variance_cache)]: DON'T MODIFY
@dataclass
class UpdateVarianceCacheIx:
    program_id: Pubkey

    # account metas
    payer: AccountMeta
    trader_risk_group: AccountMeta
    market_product_group: AccountMeta
    system_program: AccountMeta
    risk_engine_program: AccountMeta
    risk_model_configuration_acct: AccountMeta
    risk_output_register: AccountMeta
    trader_risk_state_acct: AccountMeta
    risk_and_fee_signer: AccountMeta
    remaining_accounts: Optional[List[AccountMeta]]

    def to_instruction(self):
        keys = []
        keys.append(self.payer)
        keys.append(self.trader_risk_group)
        keys.append(self.market_product_group)
        keys.append(self.system_program)
        keys.append(self.risk_engine_program)
        keys.append(self.risk_model_configuration_acct)
        keys.append(self.risk_output_register)
        keys.append(self.trader_risk_state_acct)
        keys.append(self.risk_and_fee_signer)
        if self.remaining_accounts is not None:
            keys.extend(self.remaining_accounts)

        buffer = BytesIO()
        buffer.write(InstructionTag.to_bytes(InstructionTag.UPDATE_VARIANCE_CACHE))

        return Instruction(
            accounts=keys,
            program_id=self.program_id,
            data=buffer.getvalue(),
        )

# LOCK-END


# LOCK-BEGIN[ix_fn(update_variance_cache)]: DON'T MODIFY
def update_variance_cache(
    payer: Union[str, Pubkey, AccountMeta],
    trader_risk_group: Union[str, Pubkey, AccountMeta],
    market_product_group: Union[str, Pubkey, AccountMeta],
    risk_engine_program: Union[str, Pubkey, AccountMeta],
    risk_model_configuration_acct: Union[str, Pubkey, AccountMeta],
    risk_output_register: Union[str, Pubkey, AccountMeta],
    trader_risk_state_acct: Union[str, Pubkey, AccountMeta],
    risk_and_fee_signer: Union[str, Pubkey, AccountMeta],
    system_program: Union[str, Pubkey, AccountMeta] = Pubkey.from_string("11111111111111111111111111111111"),
    remaining_accounts: Optional[List[AccountMeta]] = None,
    program_id: Optional[Pubkey] = None,
):
    if program_id is None:
        program_id = Pubkey.from_string("FUfpR31LmcP1VSbz5zDaM7nxnH55iBHkpwusgrnhaFjL")

    if isinstance(payer, (str, Pubkey)):
        payer = to_account_meta(
            payer,
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
    if isinstance(system_program, (str, Pubkey)):
        system_program = to_account_meta(
            system_program,
            is_signer=False,
            is_writable=False,
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

    return UpdateVarianceCacheIx(
        program_id=program_id,
        payer=payer,
        trader_risk_group=trader_risk_group,
        market_product_group=market_product_group,
        system_program=system_program,
        risk_engine_program=risk_engine_program,
        risk_model_configuration_acct=risk_model_configuration_acct,
        risk_output_register=risk_output_register,
        trader_risk_state_acct=trader_risk_state_acct,
        risk_and_fee_signer=risk_and_fee_signer,
        remaining_accounts=remaining_accounts,
    ).to_instruction()

# LOCK-END
