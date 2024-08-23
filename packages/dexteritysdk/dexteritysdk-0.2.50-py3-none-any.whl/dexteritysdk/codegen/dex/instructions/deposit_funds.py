# LOCK-BEGIN[imports]: DON'T MODIFY
from .instruction_tag import InstructionTag
from dataclasses import dataclass
from dexteritysdk.codegen.dex.types import DepositFundsParams
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


# LOCK-BEGIN[ix_cls(deposit_funds)]: DON'T MODIFY
@dataclass
class DepositFundsIx:
    program_id: Pubkey

    # account metas
    token_program: AccountMeta
    user: AccountMeta
    user_token_account: AccountMeta
    trader_risk_group: AccountMeta
    market_product_group: AccountMeta
    market_product_group_vault: AccountMeta
    capital_limits: AccountMeta
    remaining_accounts: Optional[List[AccountMeta]]

    # data fields
    params: DepositFundsParams

    def to_instruction(self):
        keys = []
        keys.append(self.token_program)
        keys.append(self.user)
        keys.append(self.user_token_account)
        keys.append(self.trader_risk_group)
        keys.append(self.market_product_group)
        keys.append(self.market_product_group_vault)
        keys.append(self.capital_limits)
        if self.remaining_accounts is not None:
            keys.extend(self.remaining_accounts)

        buffer = BytesIO()
        buffer.write(InstructionTag.to_bytes(InstructionTag.DEPOSIT_FUNDS))
        buffer.write(BYTES_CATALOG.pack(DepositFundsParams, self.params))

        return Instruction(
            accounts=keys,
            program_id=self.program_id,
            data=buffer.getvalue(),
        )

# LOCK-END


# LOCK-BEGIN[ix_fn(deposit_funds)]: DON'T MODIFY
def deposit_funds(
    user: Union[str, Pubkey, AccountMeta],
    user_token_account: Union[str, Pubkey, AccountMeta],
    trader_risk_group: Union[str, Pubkey, AccountMeta],
    market_product_group: Union[str, Pubkey, AccountMeta],
    market_product_group_vault: Union[str, Pubkey, AccountMeta],
    capital_limits: Union[str, Pubkey, AccountMeta],
    params: DepositFundsParams,
    token_program: Union[str, Pubkey, AccountMeta] = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
    remaining_accounts: Optional[List[AccountMeta]] = None,
    program_id: Optional[Pubkey] = None,
):
    if program_id is None:
        program_id = Pubkey.from_string("FUfpR31LmcP1VSbz5zDaM7nxnH55iBHkpwusgrnhaFjL")

    if isinstance(token_program, (str, Pubkey)):
        token_program = to_account_meta(
            token_program,
            is_signer=False,
            is_writable=False,
        )
    if isinstance(user, (str, Pubkey)):
        user = to_account_meta(
            user,
            is_signer=True,
            is_writable=False,
        )
    if isinstance(user_token_account, (str, Pubkey)):
        user_token_account = to_account_meta(
            user_token_account,
            is_signer=False,
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
    if isinstance(market_product_group_vault, (str, Pubkey)):
        market_product_group_vault = to_account_meta(
            market_product_group_vault,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(capital_limits, (str, Pubkey)):
        capital_limits = to_account_meta(
            capital_limits,
            is_signer=False,
            is_writable=False,
        )

    return DepositFundsIx(
        program_id=program_id,
        token_program=token_program,
        user=user,
        user_token_account=user_token_account,
        trader_risk_group=trader_risk_group,
        market_product_group=market_product_group,
        market_product_group_vault=market_product_group_vault,
        capital_limits=capital_limits,
        remaining_accounts=remaining_accounts,
        params=params,
    ).to_instruction()

# LOCK-END
