from solders.pubkey import Pubkey
from solders.instruction import AccountMeta, Instruction
from dexteritysdk.program_ids import SYSTEM_PROGRAM_ID as SYS_PROGRAM_ID
from podite import I64, U64, pod

from .common import InstructionCode
from dexteritysdk.program_ids import ORACLE_PROGRAM_ID


@pod
class Params:
    instr: InstructionCode
    price: I64
    decimals: U64


def initialize_oracle_ix(
    oracle_price: Pubkey, update_authority: Pubkey, price: int, decimals: int = 0
):
    keys = [
        AccountMeta(pubkey=oracle_price, is_signer=False, is_writable=True),
        AccountMeta(pubkey=update_authority, is_signer=True, is_writable=True),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    params = Params(
        instr=InstructionCode.INITIALIZE_ORACLE, price=price, decimals=decimals
    )
    return Instruction(
        accounts=keys, program_id=ORACLE_PROGRAM_ID, data=params.to_bytes()
    )
