# LOCK-BEGIN[imports]: DON'T MODIFY
from .instruction_tag import InstructionTag
from dataclasses import dataclass
from dexteritysdk.codegen.instruments.types import InitializeDerivativeParams
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


# LOCK-BEGIN[ix_cls(initialize_derivative)]: DON'T MODIFY
@dataclass
class InitializeDerivativeIx:
    program_id: Pubkey

    # account metas
    derivative_metadata: AccountMeta
    price_oracle: AccountMeta
    market_product_group: AccountMeta
    payer: AccountMeta
    system_program: AccountMeta
    authority: AccountMeta
    remaining_accounts: Optional[List[AccountMeta]]

    # data fields
    params: InitializeDerivativeParams

    def to_instruction(self):
        keys = []
        keys.append(self.derivative_metadata)
        keys.append(self.price_oracle)
        keys.append(self.market_product_group)
        keys.append(self.payer)
        keys.append(self.system_program)
        keys.append(self.authority)
        if self.remaining_accounts is not None:
            keys.extend(self.remaining_accounts)

        buffer = BytesIO()
        buffer.write(InstructionTag.to_bytes(InstructionTag.INITIALIZE_DERIVATIVE))
        buffer.write(BYTES_CATALOG.pack(InitializeDerivativeParams, self.params))

        return Instruction(
            accounts=keys,
            program_id=self.program_id,
            data=buffer.getvalue(),
        )

# LOCK-END


# LOCK-BEGIN[ix_fn(initialize_derivative)]: DON'T MODIFY
def initialize_derivative(
    derivative_metadata: Union[str, Pubkey, AccountMeta],
    price_oracle: Union[str, Pubkey, AccountMeta],
    market_product_group: Union[str, Pubkey, AccountMeta],
    payer: Union[str, Pubkey, AccountMeta],
    authority: Union[str, Pubkey, AccountMeta],
    params: InitializeDerivativeParams,
    system_program: Union[str, Pubkey, AccountMeta] = Pubkey.from_string("11111111111111111111111111111111"),
    remaining_accounts: Optional[List[AccountMeta]] = None,
    program_id: Optional[Pubkey] = None,
):
    if program_id is None:
        program_id = Pubkey.from_string("8981bZYszfz1FrFVx7gcUm61RfawMoAHnURuERRJKdkq")

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
    if isinstance(market_product_group, (str, Pubkey)):
        market_product_group = to_account_meta(
            market_product_group,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(payer, (str, Pubkey)):
        payer = to_account_meta(
            payer,
            is_signer=True,
            is_writable=True,
        )
    if isinstance(system_program, (str, Pubkey)):
        system_program = to_account_meta(
            system_program,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(authority, (str, Pubkey)):
        authority = to_account_meta(
            authority,
            is_signer=False,
            is_writable=False,
        )

    return InitializeDerivativeIx(
        program_id=program_id,
        derivative_metadata=derivative_metadata,
        price_oracle=price_oracle,
        market_product_group=market_product_group,
        payer=payer,
        system_program=system_program,
        authority=authority,
        remaining_accounts=remaining_accounts,
        params=params,
    ).to_instruction()

# LOCK-END
