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


# LOCK-BEGIN[ix_cls(settle_derivative)]: DON'T MODIFY
@dataclass
class SettleDerivativeIx:
    program_id: Pubkey

    # account metas
    market_product_group: AccountMeta
    derivative_metadata: AccountMeta
    price_oracle: AccountMeta
    dex_program: AccountMeta
    remaining_accounts: Optional[List[AccountMeta]]

    def to_instruction(self):
        keys = []
        keys.append(self.market_product_group)
        keys.append(self.derivative_metadata)
        keys.append(self.price_oracle)
        keys.append(self.dex_program)
        if self.remaining_accounts is not None:
            keys.extend(self.remaining_accounts)

        buffer = BytesIO()
        buffer.write(InstructionTag.to_bytes(InstructionTag.SETTLE_DERIVATIVE))

        return Instruction(
            accounts=keys,
            program_id=self.program_id,
            data=buffer.getvalue(),
        )

# LOCK-END


# LOCK-BEGIN[ix_fn(settle_derivative)]: DON'T MODIFY
def settle_derivative(
    market_product_group: Union[str, Pubkey, AccountMeta],
    derivative_metadata: Union[str, Pubkey, AccountMeta],
    price_oracle: Union[str, Pubkey, AccountMeta],
    dex_program: Union[str, Pubkey, AccountMeta],
    remaining_accounts: Optional[List[AccountMeta]] = None,
    program_id: Optional[Pubkey] = None,
):
    if program_id is None:
        program_id = Pubkey.from_string("8981bZYszfz1FrFVx7gcUm61RfawMoAHnURuERRJKdkq")

    if isinstance(market_product_group, (str, Pubkey)):
        market_product_group = to_account_meta(
            market_product_group,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(derivative_metadata, (str, Pubkey)):
        derivative_metadata = to_account_meta(
            derivative_metadata,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(price_oracle, (str, Pubkey)):
        price_oracle = to_account_meta(
            price_oracle,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(dex_program, (str, Pubkey)):
        dex_program = to_account_meta(
            dex_program,
            is_signer=False,
            is_writable=False,
        )

    return SettleDerivativeIx(
        program_id=program_id,
        market_product_group=market_product_group,
        derivative_metadata=derivative_metadata,
        price_oracle=price_oracle,
        dex_program=dex_program,
        remaining_accounts=remaining_accounts,
    ).to_instruction()

# LOCK-END
