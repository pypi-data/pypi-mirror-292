from podite import U8, I32, pod, Enum
from solders.pubkey import Pubkey
from solders.instruction import AccountMeta, Instruction


@pod
class InstructionCode(Enum[U8]):
    FindFees = 0
    InitializeTraderAcct = 1
    UpdateFees = 2


@pod
class NoParams:
    instr: InstructionCode


@pod
class UpdateFeesParams:
    instr: InstructionCode
    maker_fee_bps: I32
    taker_fee_bps: I32


def update_fees_ix(
    program_id: Pubkey,
    payer: Pubkey,
    fee_model_config_acct: Pubkey,
    market_product_group: Pubkey,
    system_program: Pubkey,
    maker_fee_bps: int,
    taker_fee_bps: int,
) -> Instruction:
    keys = [
        AccountMeta(pubkey=payer, is_signer=True, is_writable=False),
        AccountMeta(pubkey=fee_model_config_acct, is_signer=False, is_writable=True),
        AccountMeta(pubkey=market_product_group, is_signer=False, is_writable=False),
        AccountMeta(pubkey=system_program, is_signer=False, is_writable=False),
    ]
    return Instruction(
        accounts=keys,
        program_id=program_id,
        data=UpdateFeesParams.to_bytes(UpdateFeesParams(
            instr=InstructionCode.UpdateFees,
            maker_fee_bps=maker_fee_bps,
            taker_fee_bps=taker_fee_bps,
        )),
    )


def initialize_trader_acct_ix(
    program_id: Pubkey,
    payer: Pubkey,
    fee_model_config_acct: Pubkey,
    trader_fee_acct: Pubkey,
    market_product_group: Pubkey,
    trader_risk_group: Pubkey,
    system_program: Pubkey,
) -> Instruction:
    keys = [
        AccountMeta(pubkey=payer, is_signer=True, is_writable=False),
        AccountMeta(pubkey=fee_model_config_acct, is_signer=False, is_writable=False),
        AccountMeta(pubkey=trader_fee_acct, is_signer=False, is_writable=True),
        AccountMeta(pubkey=market_product_group, is_signer=False, is_writable=False),
        AccountMeta(pubkey=trader_risk_group, is_signer=False, is_writable=False),
        AccountMeta(pubkey=system_program, is_signer=False, is_writable=False),
    ]
    return Instruction(
        program_id=program_id,
        accounts=keys,
        data=NoParams.to_bytes(NoParams(instr=InstructionCode.InitializeTraderAcct)),
    )
