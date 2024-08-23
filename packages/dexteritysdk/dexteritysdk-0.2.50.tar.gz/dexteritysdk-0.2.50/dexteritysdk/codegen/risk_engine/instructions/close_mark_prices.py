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


# LOCK-BEGIN[ix_cls(close_mark_prices)]: DON'T MODIFY
@dataclass
class CloseMarkPricesIx:
    program_id: Pubkey

    # account metas
    payer: AccountMeta
    authority: AccountMeta
    mark_prices: AccountMeta
    market_product_group: AccountMeta
    remaining_accounts: Optional[List[AccountMeta]]

    def to_instruction(self):
        keys = []
        keys.append(self.payer)
        keys.append(self.authority)
        keys.append(self.mark_prices)
        keys.append(self.market_product_group)
        if self.remaining_accounts is not None:
            keys.extend(self.remaining_accounts)

        buffer = BytesIO()
        buffer.write(InstructionTag.to_bytes(InstructionTag.CLOSE_MARK_PRICES))

        return Instruction(
            accounts=keys,
            program_id=self.program_id,
            data=buffer.getvalue(),
        )

# LOCK-END


# LOCK-BEGIN[ix_fn(close_mark_prices)]: DON'T MODIFY
def close_mark_prices(
    payer: Union[str, Pubkey, AccountMeta],
    authority: Union[str, Pubkey, AccountMeta],
    mark_prices: Union[str, Pubkey, AccountMeta],
    market_product_group: Union[str, Pubkey, AccountMeta],
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
    if isinstance(mark_prices, (str, Pubkey)):
        mark_prices = to_account_meta(
            mark_prices,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(market_product_group, (str, Pubkey)):
        market_product_group = to_account_meta(
            market_product_group,
            is_signer=False,
            is_writable=False,
        )

    return CloseMarkPricesIx(
        program_id=program_id,
        payer=payer,
        authority=authority,
        mark_prices=mark_prices,
        market_product_group=market_product_group,
        remaining_accounts=remaining_accounts,
    ).to_instruction()

# LOCK-END
