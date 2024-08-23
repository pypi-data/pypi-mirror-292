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


# LOCK-BEGIN[ix_cls(close_trader_risk_group)]: DON'T MODIFY
@dataclass
class CloseTraderRiskGroupIx:
    program_id: Pubkey

    # account metas
    risk_engine_program: AccountMeta
    risk_signer: AccountMeta
    owner: AccountMeta
    trader_risk_group: AccountMeta
    market_product_group: AccountMeta
    trader_risk_state_acct: AccountMeta
    receiver: AccountMeta
    system_program: AccountMeta
    remaining_accounts: Optional[List[AccountMeta]]

    def to_instruction(self):
        keys = []
        keys.append(self.risk_engine_program)
        keys.append(self.risk_signer)
        keys.append(self.owner)
        keys.append(self.trader_risk_group)
        keys.append(self.market_product_group)
        keys.append(self.trader_risk_state_acct)
        keys.append(self.receiver)
        keys.append(self.system_program)
        if self.remaining_accounts is not None:
            keys.extend(self.remaining_accounts)

        buffer = BytesIO()
        buffer.write(InstructionTag.to_bytes(InstructionTag.CLOSE_TRADER_RISK_GROUP))

        return Instruction(
            accounts=keys,
            program_id=self.program_id,
            data=buffer.getvalue(),
        )

# LOCK-END


# LOCK-BEGIN[ix_fn(close_trader_risk_group)]: DON'T MODIFY
def close_trader_risk_group(
    risk_engine_program: Union[str, Pubkey, AccountMeta],
    risk_signer: Union[str, Pubkey, AccountMeta],
    owner: Union[str, Pubkey, AccountMeta],
    trader_risk_group: Union[str, Pubkey, AccountMeta],
    market_product_group: Union[str, Pubkey, AccountMeta],
    trader_risk_state_acct: Union[str, Pubkey, AccountMeta],
    receiver: Union[str, Pubkey, AccountMeta],
    system_program: Union[str, Pubkey, AccountMeta] = Pubkey.from_string("11111111111111111111111111111111"),
    remaining_accounts: Optional[List[AccountMeta]] = None,
    program_id: Optional[Pubkey] = None,
):
    if program_id is None:
        program_id = Pubkey.from_string("FUfpR31LmcP1VSbz5zDaM7nxnH55iBHkpwusgrnhaFjL")

    if isinstance(risk_engine_program, (str, Pubkey)):
        risk_engine_program = to_account_meta(
            risk_engine_program,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(risk_signer, (str, Pubkey)):
        risk_signer = to_account_meta(
            risk_signer,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(owner, (str, Pubkey)):
        owner = to_account_meta(
            owner,
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
            is_writable=False,
        )
    if isinstance(trader_risk_state_acct, (str, Pubkey)):
        trader_risk_state_acct = to_account_meta(
            trader_risk_state_acct,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(receiver, (str, Pubkey)):
        receiver = to_account_meta(
            receiver,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(system_program, (str, Pubkey)):
        system_program = to_account_meta(
            system_program,
            is_signer=False,
            is_writable=False,
        )

    return CloseTraderRiskGroupIx(
        program_id=program_id,
        risk_engine_program=risk_engine_program,
        risk_signer=risk_signer,
        owner=owner,
        trader_risk_group=trader_risk_group,
        market_product_group=market_product_group,
        trader_risk_state_acct=trader_risk_state_acct,
        receiver=receiver,
        system_program=system_program,
        remaining_accounts=remaining_accounts,
    ).to_instruction()

# LOCK-END
