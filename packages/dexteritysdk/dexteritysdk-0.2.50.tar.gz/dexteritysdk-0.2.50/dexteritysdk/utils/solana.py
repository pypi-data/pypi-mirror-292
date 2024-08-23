import base64
import json
from contextlib import contextmanager
from functools import wraps
from hashlib import sha256
from time import time, sleep
from typing import Optional, Dict
from typing import Union, Tuple, Iterable

import base58
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed, Finalized
from solana.rpc.core import RPCException, TransactionExpiredBlockheightExceededError, UnconfirmedTxError
from solana.rpc.types import TxOpts
from solders.address_lookup_table_account import AddressLookupTableAccount
from solders.instruction import AccountMeta, Instruction
from solders.message import MessageV0
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.transaction import VersionedTransaction
from solana.transaction import Transaction
from solders.transaction_status import ParsedAccount

DEX_LOG_PREFIX = "Program log: dex-log "
DEX_ORDER_SUMMARY_PREFIX = DEX_LOG_PREFIX + "new-order:order-summary "
ERROR_PREFIX = "Program log: Error: "

def calc_rent(space, client=None):
    if client is None:
        client = Context.get_global_client()
    return client.get_minimum_balance_for_rent_exemption(space).value


class Context:
    client: Optional[Client] = None
    parser: Optional["AccountParser"] = None
    signers: Dict[bytes, Tuple[Keypair, str]] = {}
    fee_payer: Optional[Keypair] = None
    raise_on_error = False
    trader_nonce: int = 0

    @staticmethod
    def init_globals(
            fee_payer: Keypair,
            client: Client,
            signers: Iterable[Tuple[Keypair, str]],
            parser: Optional["AccountParser"] = None,
            raise_on_error=False,
    ):
        Context.fee_payer = fee_payer
        Context.client = client
        Context.parser = parser
        Context.signers = {}
        Context.raise_on_error = raise_on_error
        Context.add_signers(*signers)

    @staticmethod
    def get_global_client():
        return Context.client

    @staticmethod
    def set_global_client(client):
        Context.client = client

    @staticmethod
    def get_global_parser():
        return Context.parser

    @staticmethod
    def set_global_parser(parser):
        Context.parser = parser

    @staticmethod
    def get_signers():
        return Context.signers

    # todo: rename to add signers
    @staticmethod
    def add_signers(*signers: Tuple[Keypair, str], verify=True):
        for (signer, name) in signers:
            if not isinstance(signer, Keypair) or not isinstance(name, str):
                raise ValueError(f"signers must be a list iterable of (Keypair, str) tuples. Found: {signer, name}")
            if bytes(signer.pubkey()) not in Context.signers:
                Context.signers[bytes(signer.pubkey())] = (signer, name)
        if verify:
            names = set()
            for (_, name) in Context.signers.values():
                if name in names:
                    raise ValueError("Each signer name must be unique")
                names.add(name)

    @staticmethod
    def get_global_fee_payer():
        return Context.fee_payer

    @staticmethod
    def set_global_fee_payer(fee_payer: Keypair):
        Context.fee_payer = fee_payer

    @staticmethod
    def get_raise_on_error():
        return Context.raise_on_error

    @staticmethod
    def set_raise_on_error(raise_on_error: bool):
        Context.raise_on_error = raise_on_error


@contextmanager
def global_fee_payer(fee_payer):
    old_fee_payer = Context.get_global_fee_payer()
    Context.set_global_fee_payer(fee_payer)
    yield
    Context.set_global_fee_payer(old_fee_payer)


class AccountParser:
    _parsers: Dict[bytes, callable]  # key: program_id

    def __init__(self):
        self._parsers = dict()

    def register_parser(self, program_id, parser):
        self._parsers[bytes(program_id)] = parser

    def register_parser_from_account_enum(self, program_id: Pubkey, accounts_enum):
        def parser(info):
            return accounts_enum.from_bytes(info).field

        self.register_parser(program_id, parser)

    def parse(self, owner, data):
        try:
            parser = self._parsers[bytes(owner)]
        except Exception as e:
            raise ValueError(f"Failed to find parser corresponding to account owner. Owner={owner}",
                             [str(base58.b58encode(p)) for p in self._parsers.keys()])
        return parser(data)


class TransactionDetails:
    def __init__(self, content, cluster="devnet"):
        self.content = content
        self.cluster = cluster

    def is_valid_tx(self):
        return self.content.value is not None

    @property
    def account_keys(self):
        accounts = self.content.value.transaction.transaction.message.account_keys
        account_keys = []
        for account in accounts:
            if isinstance(account, ParsedAccount):
                account_keys.append(account.pubkey())
            else:
                account_keys.append(account)
        return account_keys

    @property
    def signatures(self):
        return self.content.value.transaction.transaction.signatures

    @property
    def tx_string(self):
        return self.signatures[0]

    @property
    def log_messages(self):
        return self.content.value.transaction.meta.log_messages

    @property
    def emitted_logs(self):
        result = dict()
        for msg in self.log_messages:
            if msg.startswith(DEX_LOG_PREFIX):
                key, val = msg[len(DEX_LOG_PREFIX):].split(" ")
                result[key] = base64.b64decode(val)

        return result

    def emitted_dex_order_summaries(self):
        for msg in self.log_messages:
            if msg.startswith(DEX_ORDER_SUMMARY_PREFIX):
                yield base64.b64decode(msg[len(DEX_ORDER_SUMMARY_PREFIX):])

    @property
    def error_from_log(self):
        errs = []
        for msg in self.log_messages:
            if msg.startswith(ERROR_PREFIX):
                errs.append(msg[len(ERROR_PREFIX):])
        if len(errs) == 0:
            return None
        return errs[-1]

    @property
    def error(self):
        return self.content.value.transaction.meta.err

    def __str__(self) -> str:
        return f"TransactionDetails({self.tx_string})"

    def __repr__(self) -> str:
        return str(self)


class AccountDetails:
    def __init__(self, pubkey, content, cluster="devnet"):
        self.pubkey = pubkey
        self.content = content
        self.cluster = cluster

    def __str__(self) -> str:
        return f"AccountDetails({self.pubkey})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def slot(self):
        return self.content.context.slot

    @property
    def data(self):
        if not self.content.value:
            return None

        return self.content.value.data

    @property
    def data_obj(self):
        parser = Context.get_global_parser()
        return parser.parse(self.content.value.owner, self.content.value.data)


class MultipleAccountDetails:
    def __init__(self, pubkeys, content, cluster="devnet"):
        self.pubkeys = pubkeys
        self.content = content
        self.cluster = cluster

    def __str__(self) -> str:
        return f"MultipleAccountDetails({self.pubkeys})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def slot(self):
        return self.content.context.slot

    @property
    def data(self):
        if not self.content.value:
            return None

        return [acc_value.data for acc_value in self.content.value]

    @property
    def data_objs(self):
        parser = Context.get_global_parser()
        return [parser.parse(acc_value.owner, acc_value.data) for acc_value in self.content.value]


def fetch_transaction_details(sig, client=None):
    if client is None:
        client = Context.get_global_client()

    content = client.get_transaction(
        sig,
        encoding="json",
        commitment=Confirmed,
        max_supported_transaction_version=0,
    )
    return TransactionDetails(content)


def fetch_account_details(addr, client=None):
    if client is None:
        client = Context.get_global_client()

    content = client.get_account_info(addr, commitment=Confirmed)
    return AccountDetails(addr, content)


def fetch_multiple_account_details(addresses, client=None):
    if client is None:
        client = Context.get_global_client()

    content = client.get_multiple_accounts(addresses, commitment=Confirmed)
    return MultipleAccountDetails(addresses, content)


# only supports accounts
def explore_many(addresses):
    pubkeys = []
    for addr in addresses:
        if isinstance(addr, str):
            if len(base58.b58decode(addr)) == 64:
                raise ValueError()
            else:
                pubkeys.append(Pubkey.from_string(addr))
        elif isinstance(addr, Pubkey):
            pubkeys.append(addr)
        elif isinstance(addr, Signature):
            raise ValueError()
        else:
            raise ValueError()

    return fetch_multiple_account_details(pubkeys)


def explore(addr):
    if isinstance(addr, str):
        if len(base58.b58decode(addr)) == 64:
            kind = "tx"
            addr = Signature.from_string(addr)
        else:
            kind = "acc"
            addr = Pubkey.from_string(addr)
    elif isinstance(addr, Pubkey):
        kind = "acc"
    elif isinstance(addr, Signature):
        kind = "tx"
    else:
        raise ValueError()

    if kind == "tx":
        return fetch_transaction_details(addr)
    else:
        return fetch_account_details(addr)


def send_instructions(
        *ixs: Instruction,
        **kwargs
) -> Union[TransactionDetails, AccountDetails]:
    return send_transaction(Transaction().add(*ixs), **kwargs)


def legacy_to_v0(
        tx,
        signers,
        recent_blockhash,
        address_lookup_table_accounts,
) -> VersionedTransaction:
    msg = MessageV0.try_compile(
        payer=tx.fee_payer,
        instructions=tx.instructions,
        address_lookup_table_accounts=address_lookup_table_accounts,
        recent_blockhash=recent_blockhash
    )
    return VersionedTransaction(msg, signers)

def send_transaction(
        tx,
        *signers: Keypair,
        recent_blockhash=None,
        client=None,
        raise_on_error=None,
        confirm_tx_timeout=120,
        fetch_tx_timeout=120,
        address_lookup_table_accounts=None, # otherwise, list of AddressLookupTableAccount
        opts=None,
) -> Union[TransactionDetails, AccountDetails]:
    if fee_payer := Context.get_global_fee_payer():
        if isinstance(fee_payer, Keypair):
            tx = Transaction(fee_payer=fee_payer.pubkey()).add(tx)
        elif isinstance(fee_payer, Pubkey):
            tx = Transaction(fee_payer=fee_payer).add(tx)
        else:
            raise ValueError("fee_payer must be a Keypair or a Pubkey, but it's a {type(fee_payer)}")

    raise_on_error = raise_on_error if raise_on_error is not None else Context.get_raise_on_error()

    if len(signers) == 0:
        signers = Context.get_signers()
    else:
        signers = {bytes(signer.pubkey()): (signer, f"arg  {i}") for i, signer in enumerate(signers)}

    if client is None:
        client = Context.get_global_client()

    # filtering private keys to only contain the relevant ones
    # otherwise, there will be a problem with fee_payer
    signers_pubkeys = []
    if tx.fee_payer:
        signers_pubkeys.append(tx.fee_payer)
    for ix in tx.instructions:
        for i, meta in enumerate(ix.accounts):
            if not isinstance(meta, AccountMeta):
                print(f'{i} is {meta}')
            if meta.is_signer and meta.pubkey not in signers_pubkeys:
                signers_pubkeys.append(meta.pubkey)
    signer_keypairs = []
    for pk in signers_pubkeys:
        if bytes(pk) not in signers:
            names = [(name, str(base58.b58encode(p))) for p, (_, name) in signers.items()]
            raise ValueError(f"Required signer Pubkey not in list of Keypairs. Have {names}, want: {pk}")
        signer_keypairs.append(signers[bytes(pk)][0])

    blockhash_resp = client.get_latest_blockhash(Finalized)
    if not recent_blockhash:
        recent_blockhash = client.parse_recent_blockhash(blockhash_resp)
    last_valid_block_height = blockhash_resp.value.last_valid_block_height

    opts = opts if opts is not None else TxOpts(skip_preflight=True, skip_confirmation=True, preflight_commitment=Confirmed,
                    last_valid_block_height=last_valid_block_height)

    # print(f"address_lookup_table_accounts: {address_lookup_table_accounts}")
    # send tx without confirmation, we'll confirm manually right after with better error handling
    if address_lookup_table_accounts is not None:
        # print("converting legacy tx to v0 using ALTs")
        tx = legacy_to_v0(tx, signer_keypairs, recent_blockhash, address_lookup_table_accounts)
        result = client.send_transaction(
            tx,
            opts=opts,
        )
    else:
        result = client.send_transaction(
            tx,
            *signer_keypairs,
            opts=opts,
            recent_blockhash=recent_blockhash,
        )

    # print(f"sent tx! {result.value}")

    # try to confirm tx
    timeout = time() + confirm_tx_timeout
    while time() < timeout:
        try:
            client.confirm_transaction(
                tx_sig=result.value,
                commitment=Confirmed,
                last_valid_block_height=last_valid_block_height,
            )
            break
        except TransactionExpiredBlockheightExceededError:
            raise
        except Exception as e:
            print(f"continuing on, but failed to confirm tx with error {e}")

        blockhash_resp = client.get_latest_blockhash(Finalized)
        last_valid_block_height = blockhash_resp.value.last_valid_block_height
        sleep(0.5)
    else:
        raise UnconfirmedTxError(f"Unable to confirm transaction {result.value}")

    # try to fetch transaction data (logs etc.)
    exc = None
    timeout = time() + fetch_tx_timeout
    while time() < timeout:
        if exc:
            raise exc

        try:
            transaction_details = explore(result.value)
            if transaction_details.is_valid_tx():
                if transaction_details.error and raise_on_error:
                    try:
                        if hasattr(transaction_details.error, 'to_json'):
                            err_str = transaction_details.error.__class__.__name__ + " " + transaction_details.error.to_json()
                        else:
                            err_str = json.dumps(transaction_details.error)
                    except:
                        err_str = transaction_details.error.__class__.__name__
                    log_str = "\n".join(transaction_details.log_messages)
                    exc = ValueError(f"Transaction returned error:\n{err_str}, \nLog messages:\n{log_str}")
                    continue

                return transaction_details
            else:
                raise ValueError(f"found invalid tx. transaction_details: {transaction_details}")
        except Exception as e:
            print(f"continuing on, but failed to fetch tx details with error {e}")

        sleep(0.5)

    raise RPCException(f"Failed to fetch confirmed tx {result.value}")


def actionify(func=None, /, post_process=lambda resp: (None, resp), raise_error=False):
    assert not raise_error, "Raise_error is not implemented"

    def _actionify(make):
        @wraps(make)
        def send(*args, **kwargs):
            tx = make(*args, **kwargs)
            if tx is None:
                return post_process(None)
            if isinstance(tx, Instruction):
                tx = Transaction().add(tx)

            opts = TxOpts(
                skip_preflight=True,
                skip_confirmation=False,
                preflight_commitment=Confirmed,
            )
            response = send_transaction(
                tx,
                opts=opts,
            )
            return post_process(response)

        send.make = make
        return send

    if func is None:
        return _actionify
    return _actionify(func)


def sighash(ix_name: str) -> bytes:
    """Not technically sighash, since we don't include the arguments.
    (Because Rust doesn't allow function overloading.)
    Args:
        ix_name: The instruction name.
    Returns:
        The sighash bytes.
    """
    formatted_str = f"global:{ix_name}"
    return sha256(formatted_str.encode()).digest()[:8]


def sighash_int(ix_name: str) -> int:
    return int.from_bytes(sighash(ix_name), byteorder="little")

def get_address_lookup_table_account(pubkey) -> AddressLookupTableAccount:
    alta_account = fetch_account_details(pubkey)
    # Idiomatic, but I think this method was never implemented in solders:
    # address_lookup_table_account = AddressLookupTableAccount.from_bytes(alta_account.data)
    # So instead, we must manually construct the ALT
    addresses = []
    alta_data = alta_account.data
    for offset in range(56, len(alta_data), 32):
        pk = Pubkey.from_bytes(alta_data[offset:offset+32])
        addresses.append(pk)
    return AddressLookupTableAccount(
        key=pubkey,
        addresses=addresses
    )
