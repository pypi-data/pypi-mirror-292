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


# LOCK-BEGIN[ix_cls(initialize_covariance_matrix)]: DON'T MODIFY
@dataclass
class InitializeCovarianceMatrixIx:
    program_id: Pubkey

    # account metas
    payer: AccountMeta
    authority: AccountMeta
    covariance_metadata: AccountMeta
    correlation_matrix: AccountMeta
    market_product_group: AccountMeta
    system_program: AccountMeta
    remaining_accounts: Optional[List[AccountMeta]]

    def to_instruction(self):
        keys = []
        keys.append(self.payer)
        keys.append(self.authority)
        keys.append(self.covariance_metadata)
        keys.append(self.correlation_matrix)
        keys.append(self.market_product_group)
        keys.append(self.system_program)
        if self.remaining_accounts is not None:
            keys.extend(self.remaining_accounts)

        buffer = BytesIO()
        buffer.write(InstructionTag.to_bytes(InstructionTag.INITIALIZE_COVARIANCE_MATRIX))

        return Instruction(
            accounts=keys,
            program_id=self.program_id,
            data=buffer.getvalue(),
        )

# LOCK-END


# LOCK-BEGIN[ix_fn(initialize_covariance_matrix)]: DON'T MODIFY
def initialize_covariance_matrix(
    payer: Union[str, Pubkey, AccountMeta],
    authority: Union[str, Pubkey, AccountMeta],
    covariance_metadata: Union[str, Pubkey, AccountMeta],
    correlation_matrix: Union[str, Pubkey, AccountMeta],
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
    if isinstance(authority, (str, Pubkey)):
        authority = to_account_meta(
            authority,
            is_signer=True,
            is_writable=False,
        )
    if isinstance(covariance_metadata, (str, Pubkey)):
        covariance_metadata = to_account_meta(
            covariance_metadata,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(correlation_matrix, (str, Pubkey)):
        correlation_matrix = to_account_meta(
            correlation_matrix,
            is_signer=False,
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

    return InitializeCovarianceMatrixIx(
        program_id=program_id,
        payer=payer,
        authority=authority,
        covariance_metadata=covariance_metadata,
        correlation_matrix=correlation_matrix,
        market_product_group=market_product_group,
        system_program=system_program,
        remaining_accounts=remaining_accounts,
    ).to_instruction()

# LOCK-END
