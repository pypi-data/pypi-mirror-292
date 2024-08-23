from solders.pubkey import Pubkey
from podite import U64, pod, FixedLenArray


@pod
class MarketState:
    tag: U64
    caller_authority: Pubkey
    event_queue: Pubkey
    bids: Pubkey
    asks: Pubkey
    callback_id_len: U64
    callback_info_len: U64
    fee_budget: U64
    initial_lamports: U64
    min_base_order_size: U64
    price_bitmask: U64
    cranker_reward: U64
