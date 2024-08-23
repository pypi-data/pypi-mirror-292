# LOCK-BEGIN[imports]: DON'T MODIFY
from .instruction_tag import InstructionTag
from dataclasses import dataclass
from dexteritysdk.solmate.dtypes import Usize
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


# LOCK-BEGIN[ix_cls(remove_market_product_index_from_variance_cache)]: DON'T MODIFY
@dataclass
class RemoveMarketProductIndexFromVarianceCacheIx:
    program_id: Pubkey

    # account metas
    authority: AccountMeta
    market_product_group: AccountMeta
    trader_risk_group: AccountMeta
    covariance_metadata: AccountMeta
    variance_cache: AccountMeta
    remaining_accounts: Optional[List[AccountMeta]]

    # data fields
    market_product_index: Usize

    def to_instruction(self):
        keys = []
        keys.append(self.authority)
        keys.append(self.market_product_group)
        keys.append(self.trader_risk_group)
        keys.append(self.covariance_metadata)
        keys.append(self.variance_cache)
        if self.remaining_accounts is not None:
            keys.extend(self.remaining_accounts)

        buffer = BytesIO()
        buffer.write(InstructionTag.to_bytes(InstructionTag.REMOVE_MARKET_PRODUCT_INDEX_FROM_VARIANCE_CACHE))
        buffer.write(BYTES_CATALOG.pack(Usize, self.market_product_index))

        return Instruction(
            accounts=keys,
            program_id=self.program_id,
            data=buffer.getvalue(),
        )

# LOCK-END


# LOCK-BEGIN[ix_fn(remove_market_product_index_from_variance_cache)]: DON'T MODIFY
def remove_market_product_index_from_variance_cache(
    authority: Union[str, Pubkey, AccountMeta],
    market_product_group: Union[str, Pubkey, AccountMeta],
    trader_risk_group: Union[str, Pubkey, AccountMeta],
    covariance_metadata: Union[str, Pubkey, AccountMeta],
    variance_cache: Union[str, Pubkey, AccountMeta],
    market_product_index: Usize,
    remaining_accounts: Optional[List[AccountMeta]] = None,
    program_id: Optional[Pubkey] = None,
):
    if program_id is None:
        program_id = Pubkey.from_string("92wdgEqyiDKrcbFHoBTg8HxMj932xweRCKaciGSW3uMr")

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
    if isinstance(trader_risk_group, (str, Pubkey)):
        trader_risk_group = to_account_meta(
            trader_risk_group,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(covariance_metadata, (str, Pubkey)):
        covariance_metadata = to_account_meta(
            covariance_metadata,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(variance_cache, (str, Pubkey)):
        variance_cache = to_account_meta(
            variance_cache,
            is_signer=False,
            is_writable=True,
        )

    return RemoveMarketProductIndexFromVarianceCacheIx(
        program_id=program_id,
        authority=authority,
        market_product_group=market_product_group,
        trader_risk_group=trader_risk_group,
        covariance_metadata=covariance_metadata,
        variance_cache=variance_cache,
        remaining_accounts=remaining_accounts,
        market_product_index=market_product_index,
    ).to_instruction()

# LOCK-END
