import os
import json
import re
import subprocess
from functools import partial
from typing import Callable, Dict, Union, Set

import solders
from solders.pubkey import Pubkey
from dexteritysdk.solmate.anchor import Idl
from dexteritysdk.solmate.anchor.codegen import usize_type, unix_timestamp_type, program_error_type, CodeGen
from dexteritysdk.solmate.anchor.editor import CodeEditor
from dexteritysdk.solmate.utils import pascal_to_snake
from spl.token.constants import TOKEN_PROGRAM_ID

from dexteritysdk.scripts.extract_program_ids import get_root


def main():
    root = get_root()
    cli(idl_dir=f'{root}/target/idl', out_dir=f'{root}/client', pids_dir=f'{root}/target/deploy',
        parent_module='dexteritysdk.codegen', skip_types={"TwoIterators", "DomainOrProgramError"})


if __name__ == '__main__':
    main()


def side_type(editor: CodeEditor):
    editor.add_from_import("dexteritysdk.utils.aob.state.base", "Side")
    return "Side"


def self_trade_behavior_type(editor: CodeEditor):
    editor.add_from_import("dexteritysdk.utils.aob.state.base", "SelfTradeBehavior")
    return "SelfTradeBehavior"


def cli(
        idl_dir: str,
        out_dir: str,
        pids_dir: Union[str, Dict[str, Pubkey]],
        parent_module: str,
        skip_types: Set[str],
):
    protocol_to_idl_and_types = {}
    protocol_to_pid = get_protocols(idl_dir, pids_dir)
    for protocol in protocol_to_pid.keys():
        idl = Idl.from_json_file(f"{idl_dir}/{protocol}.json")

        idl.types = list(filter(lambda x: x.name not in skip_types, idl.types))
        idl.accounts = list(filter(lambda x: x.name not in skip_types, idl.accounts))
        protocol_to_idl_and_types[protocol] = (
            idl,
            defined_types_to_imports(f"{parent_module}.{protocol}", idl),
        )

        if protocol.upper() in os.environ:
            env_pid = os.environ[protocol.upper()]
            print(f"Using program_id from ENV for {protocol}: {env_pid}")
            protocol_to_pid[protocol] = env_pid
        else:
            print(f"Using program_id from target/deploy/{protocol}-keypair.json for {protocol}: "
                  f"{protocol_to_pid[protocol]}")

        if protocol_to_pid[protocol] is None:
            raise Exception("Found IDL but no program id set")

    external_types = {
        "usize": usize_type,
        "UnixTimestamp": unix_timestamp_type,
        "ProgramError": program_error_type,
        "SelfTradeBehavior": self_trade_behavior_type,
        "Side": side_type,
    }
    # allow each IDL to reference types defined in other IDLs
    for (_, exported_types) in protocol_to_idl_and_types.values():
        external_types.update(exported_types)

    for protocol, (idl, _) in protocol_to_idl_and_types.items():
        print(f"Generating code for {protocol}")
        codegen = CodeGen(
            idl=idl,
            addresses={},
            root_module=f"{parent_module}.{protocol}",
            source_path=out_dir,
            external_types=external_types,
            default_accounts={
                "systemProgram": solders.system_program.ID,
                "token_program": Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
                "sysvar_rent": solders.sysvar.RENT,
                "program_id": protocol_to_pid[protocol],
            },
            accnt_tag_values="anchor",
            instr_tag_values="anchor",
            skip_types=skip_types,
        )
        codegen.generate_code(check_missing_types=not True)
        codegen.save_modules()


def defined_types_to_imports(
        root_module: str, idl: Idl
) -> Dict[str, Callable[[CodeEditor], str]]:
    def add_import(name: str, editor: CodeEditor) -> str:
        editor.add_from_import(f"{root_module}.types.{pascal_to_snake(name)}", name)
        return name

    type_definitions = idl.types + idl.accounts
    return dict(((ty.name, partial(add_import, ty.name)) for ty in type_definitions))


def get_protocols(idl_dir: str, pids: Union[str, Dict[str, str]]) -> Dict[str, str]:
    protocols = set()
    for filename in os.listdir(idl_dir):
        match = re.search(r"([a-z_\-]+).json", filename)
        if match is None:
            continue
        protocol = match.groups()[0]
        protocols.add(protocol)

    # if a path was passed in, load pids from the directory
    if isinstance(pids, str):
        pids = dir_to_pids(pids)

    intersection = {}
    for protocol, pid in pids.items():
        if protocol in protocols:
            intersection[protocol] = pid
    for protocol in protocols:
        if protocol not in pids:
            print("WARNING: found idl file with no matching program id: ", protocol)
            intersection[protocol] = None

    return intersection


def dir_to_pids(dir: str) -> Dict[str, str]:
    program_to_id = {}
    root = run("git rev-parse --show-toplevel")
    for filename in os.listdir(dir):
        match = re.search(r"([a-z_]+)-keypair.json", filename)
        if match is None:
            continue
        program = match.groups()[0]
        program_to_id[program] = run(f"solana-keygen pubkey {dir}/{filename}")
    return program_to_id


def run(cmd, debug=False):
    if debug:
        print(cmd)
    res = subprocess.check_output(cmd, shell=True).strip().decode("utf-8")
    if debug:
        print(res)
    return res
