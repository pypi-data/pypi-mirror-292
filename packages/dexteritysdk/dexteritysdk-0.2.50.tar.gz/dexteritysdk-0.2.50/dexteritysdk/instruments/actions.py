from typing import List
from dexteritysdk.program_ids import DEX_PROGRAM_ID, INSTRUMENTS_PROGRAM_ID

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.transaction import Transaction

import dexteritysdk.instruments.instructions as ixs

from dexteritysdk.codegen.dex.types import Fractional
from dexteritysdk.codegen.instruments import instructions as iixs
from dexteritysdk.codegen.instruments import types as its
from dexteritysdk.utils.solana import (
    actionify,
    Context,
)
from dexteritysdk.codegen.instruments.types import (
    InstrumentType,
    OracleType,
)


def _calc_rent(space, client=None):
    if client is None:
        client = Context.get_global_client()
    return client.get_minimum_balance_for_rent_exemption(space)["result"]


def extract_acct_addr(resp, idx=0):
    addr = resp.instructions[0]["accounts"][idx]
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


@actionify(post_process=lambda x: extract_acct_addr(x, idx=0))
def initialize_derivative(
    price_oracle: Pubkey,
    market_product_group: Pubkey,
    payer: Pubkey,
    instrument_type: InstrumentType,
    strike: float,
    full_funding_period: int,
    minimum_funding_period: int,
    initialization_time: int,
    oracle_type: OracleType,
    close_authority: Pubkey,
    clock: Pubkey = None,
    **kwargs,
):
    params = its.InitializeDerivativeParams(
        instrument_type=instrument_type,
        strike=Fractional.to_decimal(strike),
        full_funding_period=full_funding_period,
        minimum_funding_period=minimum_funding_period,
        initialization_time=initialization_time,
        close_authority=close_authority,
        oracle_type=oracle_type,
    )
    return Transaction().add(
        iixs.initialize_derivative(
            derivative_metadata=ixs.get_derivative_key(
                price_oracle=price_oracle,
                market_product_group=market_product_group,
                instrument_type=instrument_type,
                strike=strike,
                full_funding_period=full_funding_period,
                minimum_funding_period=minimum_funding_period,
                initialization_time=initialization_time,
            )[0],
            price_oracle=price_oracle,
            market_product_group=market_product_group,
            payer=payer,
            clock=clock,
            params=params,
        ),
    )


@actionify(post_process=lambda x: extract_acct_addr(x, idx=0))
def initialize_fixed_income(
    face_value: int,
    market_product_group: Pubkey,
    payer: Keypair,
    coupon_dates: List[int],
    coupon_rate: int,
    maturity_date: int,
    initialization_time: int,
    close_authority: Pubkey,
):
    return iixs.initialize_fixed_income(
        fixed_income_metadata=ixs.get_fixed_income_key(
            market_product_group=market_product_group,
            initialization_time=initialization_time,
            coupon_rate=coupon_rate,
            maturity_date=maturity_date
        )[0],
        market_product_group=market_product_group,
        payer=payer.pubkey(),
        params=its.InitializeFixedIncomeParams(
            face_value=face_value,
            coupon_rate=coupon_rate,
            initialization_time=initialization_time,
            coupon_dates=coupon_dates,
            maturity_date=maturity_date,
            close_authority=close_authority,
        )
    )


_tick = 0
@actionify
def settle_derivative(
    market_product_group: Pubkey,
    derivative_metadata: Pubkey,
    payer: Pubkey,
    price_oracle: Pubkey,
    clock: Pubkey = None,
):
    _tick += 1
    return Transaction(fee_payer=payer).add(
        iixs.settle_derivative(
            market_product_group,
            derivative_metadata=derivative_metadata,
            price_oracle=price_oracle,
            clock=clock,
            dex_program=DEX_PROGRAM_ID,
            tick=_tick,
        ),
    )


@actionify(post_process=lambda x: extract_acct_addr(x, idx=1))
def settle_fixed_income_ix(
    market_product_group: Pubkey,
    fixed_income_metadata: Pubkey,
):
    return iixs.settle_fixed_income(
        market_product_group=market_product_group,
        fixed_income_metadata=fixed_income_metadata,
        dex_program=DEX_PROGRAM_ID,
    )
