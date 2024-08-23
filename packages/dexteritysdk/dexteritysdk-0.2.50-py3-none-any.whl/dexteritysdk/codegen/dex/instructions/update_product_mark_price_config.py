# LOCK-BEGIN[imports]: DON'T MODIFY
from .instruction_tag import InstructionTag
from dataclasses import dataclass
from dexteritysdk.codegen.dex.types import UpdateProductMarkPriceConfigParams
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


# LOCK-BEGIN[ix_cls(update_product_mark_price_config)]: DON'T MODIFY
@dataclass
class UpdateProductMarkPriceConfigIx:
    program_id: Pubkey

    # account metas
    authority: AccountMeta
    market_product_group: AccountMeta
    product: AccountMeta
    remaining_accounts: Optional[List[AccountMeta]]

    # data fields
    params: UpdateProductMarkPriceConfigParams

    def to_instruction(self):
        keys = []
        keys.append(self.authority)
        keys.append(self.market_product_group)
        keys.append(self.product)
        if self.remaining_accounts is not None:
            keys.extend(self.remaining_accounts)

        buffer = BytesIO()
        buffer.write(InstructionTag.to_bytes(InstructionTag.UPDATE_PRODUCT_MARK_PRICE_CONFIG))
        buffer.write(BYTES_CATALOG.pack(UpdateProductMarkPriceConfigParams, self.params))

        return Instruction(
            accounts=keys,
            program_id=self.program_id,
            data=buffer.getvalue(),
        )

# LOCK-END


# LOCK-BEGIN[ix_fn(update_product_mark_price_config)]: DON'T MODIFY
def update_product_mark_price_config(
    authority: Union[str, Pubkey, AccountMeta],
    market_product_group: Union[str, Pubkey, AccountMeta],
    product: Union[str, Pubkey, AccountMeta],
    params: UpdateProductMarkPriceConfigParams,
    remaining_accounts: Optional[List[AccountMeta]] = None,
    program_id: Optional[Pubkey] = None,
):
    if program_id is None:
        program_id = Pubkey.from_string("FUfpR31LmcP1VSbz5zDaM7nxnH55iBHkpwusgrnhaFjL")

    if isinstance(authority, (str, Pubkey)):
        authority = to_account_meta(
            authority,
            is_signer=True,
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

    return UpdateProductMarkPriceConfigIx(
        program_id=program_id,
        authority=authority,
        market_product_group=market_product_group,
        product=product,
        remaining_accounts=remaining_accounts,
        params=params,
    ).to_instruction()

# LOCK-END
