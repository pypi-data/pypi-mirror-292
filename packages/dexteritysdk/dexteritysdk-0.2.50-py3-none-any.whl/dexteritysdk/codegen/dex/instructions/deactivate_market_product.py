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


# LOCK-BEGIN[ix_cls(deactivate_market_product)]: DON'T MODIFY
@dataclass
class DeactivateMarketProductIx:
    program_id: Pubkey

    # account metas
    authority: AccountMeta
    market_product_group: AccountMeta
    product: AccountMeta
    aaob_program: AccountMeta
    orderbook: AccountMeta
    market_signer: AccountMeta
    event_queue: AccountMeta
    bids: AccountMeta
    asks: AccountMeta
    remaining_accounts: Optional[List[AccountMeta]]

    def to_instruction(self):
        keys = []
        keys.append(self.authority)
        keys.append(self.market_product_group)
        keys.append(self.product)
        keys.append(self.aaob_program)
        keys.append(self.orderbook)
        keys.append(self.market_signer)
        keys.append(self.event_queue)
        keys.append(self.bids)
        keys.append(self.asks)
        if self.remaining_accounts is not None:
            keys.extend(self.remaining_accounts)

        buffer = BytesIO()
        buffer.write(InstructionTag.to_bytes(InstructionTag.DEACTIVATE_MARKET_PRODUCT))

        return Instruction(
            accounts=keys,
            program_id=self.program_id,
            data=buffer.getvalue(),
        )

# LOCK-END


# LOCK-BEGIN[ix_fn(deactivate_market_product)]: DON'T MODIFY
def deactivate_market_product(
    authority: Union[str, Pubkey, AccountMeta],
    market_product_group: Union[str, Pubkey, AccountMeta],
    product: Union[str, Pubkey, AccountMeta],
    aaob_program: Union[str, Pubkey, AccountMeta],
    orderbook: Union[str, Pubkey, AccountMeta],
    market_signer: Union[str, Pubkey, AccountMeta],
    event_queue: Union[str, Pubkey, AccountMeta],
    bids: Union[str, Pubkey, AccountMeta],
    asks: Union[str, Pubkey, AccountMeta],
    remaining_accounts: Optional[List[AccountMeta]] = None,
    program_id: Optional[Pubkey] = None,
):
    if program_id is None:
        program_id = Pubkey.from_string("FUfpR31LmcP1VSbz5zDaM7nxnH55iBHkpwusgrnhaFjL")

    if isinstance(authority, (str, Pubkey)):
        authority = to_account_meta(
            authority,
            is_signer=False,
            is_writable=True,
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
    if isinstance(aaob_program, (str, Pubkey)):
        aaob_program = to_account_meta(
            aaob_program,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(orderbook, (str, Pubkey)):
        orderbook = to_account_meta(
            orderbook,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(market_signer, (str, Pubkey)):
        market_signer = to_account_meta(
            market_signer,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(event_queue, (str, Pubkey)):
        event_queue = to_account_meta(
            event_queue,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(bids, (str, Pubkey)):
        bids = to_account_meta(
            bids,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(asks, (str, Pubkey)):
        asks = to_account_meta(
            asks,
            is_signer=False,
            is_writable=True,
        )

    return DeactivateMarketProductIx(
        program_id=program_id,
        authority=authority,
        market_product_group=market_product_group,
        product=product,
        aaob_program=aaob_program,
        orderbook=orderbook,
        market_signer=market_signer,
        event_queue=event_queue,
        bids=bids,
        asks=asks,
        remaining_accounts=remaining_accounts,
    ).to_instruction()

# LOCK-END
