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


# LOCK-BEGIN[ix_cls(update_trader_funding)]: DON'T MODIFY
@dataclass
class UpdateTraderFundingIx:
    program_id: Pubkey

    # account metas
    market_product_group: AccountMeta
    trader_risk_group: AccountMeta
    risk_engine_program: AccountMeta
    risk_output_register: AccountMeta
    trader_risk_state_account_info: AccountMeta
    risk_model_configuration_acct: AccountMeta
    risk_signer: AccountMeta
    remaining_accounts: Optional[List[AccountMeta]]

    def to_instruction(self):
        keys = []
        keys.append(self.market_product_group)
        keys.append(self.trader_risk_group)
        keys.append(self.risk_engine_program)
        keys.append(self.risk_output_register)
        keys.append(self.trader_risk_state_account_info)
        keys.append(self.risk_model_configuration_acct)
        keys.append(self.risk_signer)
        if self.remaining_accounts is not None:
            keys.extend(self.remaining_accounts)

        buffer = BytesIO()
        buffer.write(InstructionTag.to_bytes(InstructionTag.UPDATE_TRADER_FUNDING))

        return Instruction(
            accounts=keys,
            program_id=self.program_id,
            data=buffer.getvalue(),
        )

# LOCK-END


# LOCK-BEGIN[ix_fn(update_trader_funding)]: DON'T MODIFY
def update_trader_funding(
    market_product_group: Union[str, Pubkey, AccountMeta],
    trader_risk_group: Union[str, Pubkey, AccountMeta],
    risk_engine_program: Union[str, Pubkey, AccountMeta],
    risk_output_register: Union[str, Pubkey, AccountMeta],
    trader_risk_state_account_info: Union[str, Pubkey, AccountMeta],
    risk_model_configuration_acct: Union[str, Pubkey, AccountMeta],
    risk_signer: Union[str, Pubkey, AccountMeta],
    remaining_accounts: Optional[List[AccountMeta]] = None,
    program_id: Optional[Pubkey] = None,
):
    if program_id is None:
        program_id = Pubkey.from_string("FUfpR31LmcP1VSbz5zDaM7nxnH55iBHkpwusgrnhaFjL")

    if isinstance(market_product_group, (str, Pubkey)):
        market_product_group = to_account_meta(
            market_product_group,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(trader_risk_group, (str, Pubkey)):
        trader_risk_group = to_account_meta(
            trader_risk_group,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(risk_engine_program, (str, Pubkey)):
        risk_engine_program = to_account_meta(
            risk_engine_program,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(risk_output_register, (str, Pubkey)):
        risk_output_register = to_account_meta(
            risk_output_register,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(trader_risk_state_account_info, (str, Pubkey)):
        trader_risk_state_account_info = to_account_meta(
            trader_risk_state_account_info,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(risk_model_configuration_acct, (str, Pubkey)):
        risk_model_configuration_acct = to_account_meta(
            risk_model_configuration_acct,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(risk_signer, (str, Pubkey)):
        risk_signer = to_account_meta(
            risk_signer,
            is_signer=False,
            is_writable=False,
        )

    return UpdateTraderFundingIx(
        program_id=program_id,
        market_product_group=market_product_group,
        trader_risk_group=trader_risk_group,
        risk_engine_program=risk_engine_program,
        risk_output_register=risk_output_register,
        trader_risk_state_account_info=trader_risk_state_account_info,
        risk_model_configuration_acct=risk_model_configuration_acct,
        risk_signer=risk_signer,
        remaining_accounts=remaining_accounts,
    ).to_instruction()

# LOCK-END
