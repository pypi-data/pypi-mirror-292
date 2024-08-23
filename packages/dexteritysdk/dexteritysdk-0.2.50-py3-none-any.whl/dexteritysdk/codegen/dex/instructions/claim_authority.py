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


# LOCK-BEGIN[ix_cls(claim_authority)]: DON'T MODIFY
@dataclass
class ClaimAuthorityIx:
    program_id: Pubkey

    # account metas
    market_product_group: AccountMeta
    new_authority: AccountMeta
    remaining_accounts: Optional[List[AccountMeta]]

    def to_instruction(self):
        keys = []
        keys.append(self.market_product_group)
        keys.append(self.new_authority)
        if self.remaining_accounts is not None:
            keys.extend(self.remaining_accounts)

        buffer = BytesIO()
        buffer.write(InstructionTag.to_bytes(InstructionTag.CLAIM_AUTHORITY))

        return Instruction(
            accounts=keys,
            program_id=self.program_id,
            data=buffer.getvalue(),
        )

# LOCK-END


# LOCK-BEGIN[ix_fn(claim_authority)]: DON'T MODIFY
def claim_authority(
    market_product_group: Union[str, Pubkey, AccountMeta],
    new_authority: Union[str, Pubkey, AccountMeta],
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
    if isinstance(new_authority, (str, Pubkey)):
        new_authority = to_account_meta(
            new_authority,
            is_signer=True,
            is_writable=False,
        )

    return ClaimAuthorityIx(
        program_id=program_id,
        market_product_group=market_product_group,
        new_authority=new_authority,
        remaining_accounts=remaining_accounts,
    ).to_instruction()

# LOCK-END
