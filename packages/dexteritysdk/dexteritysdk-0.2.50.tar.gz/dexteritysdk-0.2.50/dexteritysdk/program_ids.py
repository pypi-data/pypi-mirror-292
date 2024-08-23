import os

import solders.system_program
import solders.sysvar
import spl.token.constants
from solders.pubkey import Pubkey

from dexteritysdk.scripts import extract_program_ids

try:
    programs = extract_program_ids.get_program_to_id()
except:
    programs = {}

RENT_PROGRAM_ID = solders.sysvar.RENT
CLOCK_PROGRAM_ID = solders.sysvar.CLOCK
SYSTEM_PROGRAM_ID = solders.system_program.ID
SPL_TOKEN_PROGRAM_ID = spl.token.constants.TOKEN_PROGRAM_ID

DEX_PROGRAM_ID = Pubkey.from_string(
    os.environ.get("DEX", programs.get("dex", "FUfpR31LmcP1VSbz5zDaM7nxnH55iBHkpwusgrnhaFjL"))
)
INSTRUMENTS_PROGRAM_ID = Pubkey.from_string(
    os.environ.get("INSTRUMENTS", programs.get("instruments", "8981bZYszfz1FrFVx7gcUm61RfawMoAHnURuERRJKdkq"))
)
ORACLE_PROGRAM_ID = Pubkey.from_string(
    os.environ.get("DUMMY_ORACLE", programs.get("dummy_oracle", "GLkqj95yBQHqb42A7Lf5bK33NBRnH4LhACVWajjyrgv4"))
)
STAKING_PROGRAM_ID = Pubkey.from_string(
    os.environ.get("STAKING", programs.get("staking", "2jmux3fWV5zHirkEZCoSMEgTgdYZqkE9Qx2oQnxoHRgA"))
)
# NOOP_RISK_ENGINE_PROGRAM_ID = Pubkey.from_string(
#     os.environ.get("NOOP_RISK_ENGINE", programs.get("noop_risk_engine", ""))
# )
# SIMPLE_RISK_ENGINE_PROGRAM_ID = Pubkey.from_string(
#     os.environ.get("SIMPLE_RISK_ENGINE", "4HzqJ5fXcE5W1YTLa8m6M3cdSuGGjuBmDy9zNSTSnkJY")  # todo remove
# )
# ALPHA_RISK_ENGINE_PROGRAM_ID = Pubkey.from_string(
#     os.environ.get("ALPHA_RISK_ENGINE", programs.get("alpha_risk_engine", ""))
# )

# this is to get things going as this is imported in a few places but seems unused
ALPHA_RISK_ENGINE_PROGRAM_ID = Pubkey.default()

RISK_ENGINE_PROGRAM_ID = Pubkey.from_string(
    os.environ.get("RISK_ENGINE", "92wdgEqyiDKrcbFHoBTg8HxMj932xweRCKaciGSW3uMr")
)
AOB_PROGRAM_ID = Pubkey.from_string(
    os.environ.get("AGNOSTIC_ORDERBOOK",
                   programs.get("agnostic_orderbook", "DchhQ6g8LyRCM5mnao1MAg3g9twfqBbDmUWgpQpFfn1b"))
)
CONSTANT_FEES_MODEL_PROGRAM_ID = Pubkey.from_string(
    os.environ.get("CONSTANT_FEES", programs.get("constant_fees", "5AZioCPiC7uZ4zRmkKSg5nsb2A98RhmW89a1pMwiDoeT"))
)
INCENTIVE_PROGRAM_ID = Pubkey.from_string(
    os.environ.get("INCENTIVE", programs.get("incentive", "5u8mLVnUSQNSbKdZPNGTfWHGwV5uJh9by5Fa6jb6BP6h"))
)

# todo: make this ~better~ -> work...
# set_pid_by_protocol_name("risk", ALPHA_RISK_ENGINE_PROGRAM_ID)
# set_pid_by_protocol_name("dex", DEX_PROGRAM_ID)
# set_pid_by_protocol_name("instruments", INSTRUMENTS_PROGRAM_ID)
