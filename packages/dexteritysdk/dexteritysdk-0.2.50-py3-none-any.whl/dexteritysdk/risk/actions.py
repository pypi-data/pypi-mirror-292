from ctypes import Union
from solders.instruction import AccountMeta, Instruction
from typing import Optional

from solders.pubkey import Pubkey
from solana.transaction import Transaction
import dexteritysdk.program_ids as pids
from podite import pod, U64
from dexteritysdk.utils.solana import (
    actionify
)
from dexteritysdk.dex.actions import RISK_CONFIG_LAYOUT
from dexteritysdk.dex.addrs import get_risk_register_addr

@pod
class Params:
    instr: U64

def _post_init_risk_config(resp):
    if resp is None:
        return None, None
    addr = resp.instructions[0]["accounts"][1]
    exists = False

    if resp.error:
        error_ix, error_info = resp.error["InstructionError"]
        if error_ix == 0 and error_info["Custom"] == 0:
            exists = True
    else:
        exists = True

    if exists:
        return addr, resp
    else:
        return None, resp


@actionify(post_process=_post_init_risk_config)
def initialize_risk_config_acct(
    admin: Pubkey,
    market_product_group: Pubkey,
    program_id: Optional[Pubkey] = pids.ALPHA_RISK_ENGINE_PROGRAM_ID,
    risk_model_config_acct: Optional[Pubkey] = None,
    layout_str: Optional[str] = RISK_CONFIG_LAYOUT,
):
    if program_id == pids.ALPHA_RISK_ENGINE_PROGRAM_ID: 
        return None

    if risk_model_config_acct is None:
        risk_model_config_acct = get_risk_register_addr(admin, market_product_group, program_id, layout_str)

    keys = [
        AccountMeta(pubkey=market_product_group, is_signer=False, is_writable=False),
        AccountMeta(pubkey=admin, is_signer=True, is_writable=False),
        AccountMeta(pubkey=risk_model_config_acct, is_signer=False, is_writable=True),        
    ]

    params = Params(
        instr=4,
    )

    return Transaction(fee_payer=admin).add(
        Instruction(
                accounts=keys,
                program_id=program_id,
                data=Params.to_bytes(params),
            ),
        )

