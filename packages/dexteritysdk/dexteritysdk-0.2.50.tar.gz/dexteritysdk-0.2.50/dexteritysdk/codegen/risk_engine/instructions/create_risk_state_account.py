# LOCK-BEGIN[imports]: DON'T MODIFY
from .instruction_tag import InstructionTag
from dataclasses import dataclass
from dexteritysdk.solmate.utils import to_account_meta
from io import BytesIO
from podite import BYTES_CATALOG
from solders.pubkey import Pubkey
from solders.instruction import (
    AccountMeta,
    Instruction,
)
from typing import (
    List,
    Optional,
    Union,
)

# LOCK-END


# LOCK-BEGIN[ix_cls(create_risk_state_account)]: DON'T MODIFY
@dataclass
class CreateRiskStateAccountIx:
    program_id: Pubkey

    # account metas
    payer: AccountMeta
    risk_signer: AccountMeta
    variance_cache: AccountMeta
    market_product_group: AccountMeta
    system_program: AccountMeta
    remaining_accounts: Optional[List[AccountMeta]]

    def to_instruction(self):
        keys = []
        keys.append(self.payer)
        keys.append(self.risk_signer)
        keys.append(self.variance_cache)
        keys.append(self.market_product_group)
        keys.append(self.system_program)
        if self.remaining_accounts is not None:
            keys.extend(self.remaining_accounts)

        buffer = BytesIO()
        buffer.write(InstructionTag.to_bytes(InstructionTag.CREATE_RISK_STATE_ACCOUNT))

        return Instruction(
            accounts=keys,
            program_id=self.program_id,
            data=buffer.getvalue(),
        )

# LOCK-END


# LOCK-BEGIN[ix_fn(create_risk_state_account)]: DON'T MODIFY
def create_risk_state_account(
    payer: Union[str, Pubkey, AccountMeta],
    risk_signer: Union[str, Pubkey, AccountMeta],
    variance_cache: Union[str, Pubkey, AccountMeta],
    market_product_group: Union[str, Pubkey, AccountMeta],
    system_program: Union[str, Pubkey, AccountMeta] = Pubkey.from_string("11111111111111111111111111111111"),
    remaining_accounts: Optional[List[AccountMeta]] = None,
    program_id: Optional[Pubkey] = None,
):
    if program_id is None:
        program_id = Pubkey.from_string("92wdgEqyiDKrcbFHoBTg8HxMj932xweRCKaciGSW3uMr")

    if isinstance(payer, (str, Pubkey)):
        payer = to_account_meta(
            payer,
            is_signer=True,
            is_writable=True,
        )
    if isinstance(risk_signer, (str, Pubkey)):
        risk_signer = to_account_meta(
            risk_signer,
            is_signer=True,
            is_writable=False,
        )
    if isinstance(variance_cache, (str, Pubkey)):
        variance_cache = to_account_meta(
            variance_cache,
            is_signer=True,
            is_writable=True,
        )
    if isinstance(market_product_group, (str, Pubkey)):
        market_product_group = to_account_meta(
            market_product_group,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(system_program, (str, Pubkey)):
        system_program = to_account_meta(
            system_program,
            is_signer=False,
            is_writable=False,
        )

    return CreateRiskStateAccountIx(
        program_id=program_id,
        payer=payer,
        risk_signer=risk_signer,
        variance_cache=variance_cache,
        market_product_group=market_product_group,
        system_program=system_program,
        remaining_accounts=remaining_accounts,
    ).to_instruction()

# LOCK-END
