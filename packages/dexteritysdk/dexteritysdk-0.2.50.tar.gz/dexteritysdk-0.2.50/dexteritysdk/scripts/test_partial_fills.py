import json
from random import random
import sys
import time

print('importing dexterity (it takes a while)...', end='', flush=True)
from dexteritysdk.dex.sdk_context import SDKContext, SDKTrader
from dexteritysdk.utils.aob import Side
print('success')
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey


CRANK_SLEEP_SECONDS = 5
BTC_PRICE = 69000
ETH_PRICE = 4000
SOL_PRICE = 150


def load_keypair(fp):
    with open(fp, "r") as f:
        kp = json.load(f)
    return Keypair.from_bytes(kp)

async def main():
    network = "http://localhost:8899/"
    client = Client(network)

    print('loading keypairs...', end='', flush=True)
    keypair = load_keypair('../deploy_key.json')
    mpg_keypair = load_keypair('../target/deploy/mpg-keypair.json')
    print('success')

    print('connecting...', end='', flush=True)
    ctx = SDKContext.connect(
	client=client,
	market_product_group_key=mpg_keypair.pubkey(),
	payer=keypair,
	raise_on_error=True
    )
    print('success')

    print('creating maker trg...', end='', flush=True)
    maker = ctx.register_trader(keypair)
    print('success (maker trg pubkey: {})'.format(maker.account))
    print('subscribing...', end='', flush=True)
    asyncio.create_task(maker.subscribe(ctx, 'ws://localhost:8900',
                                        fills_callback=lambda fill, event_type: print(f"saw fill event {event_type} {fill}")))
    await asyncio.sleep(1)
    print('success')

    print('creating taker trg...', end='', flush=True)
    taker = ctx.register_trader(keypair)
    asyncio.create_task(taker.subscribe(ctx, 'ws://localhost:8900'))
    print('success (taker trg pubkey: {})'.format(taker.account))

    INITIAL_DEPOSIT = 100000
    print('maker depositing 100k USDC...', end='', flush=True)
    maker.deposit(ctx, INITIAL_DEPOSIT)
    print('success')
    print('taker depositing 100k USDC...', end='', flush=True)
    taker.deposit(ctx, INITIAL_DEPOSIT)
    print('success')

    print('checking balance...', end='', flush=True)
    maker_trg, _ = maker.get_trader_risk_group()
    if maker_trg.cash_balance.value != INITIAL_DEPOSIT:
        raise RuntimeError(f"expected maker_trg.cash_balance == {INITIAL_DEPOSIT}, got {maker_trg.cash_balance}")
    taker_trg, _ = taker.get_trader_risk_group()
    if taker_trg.cash_balance.value != INITIAL_DEPOSIT:
        raise RuntimeError(f"expected taker_trg.cash_balance == {INITIAL_DEPOSIT}, got {taker_trg.cash_balance}")
    print('success')

    size, price = 0.1, BTC_PRICE

    product = ctx.products[0]

    client_order_id = int(random() * 1e6)
    print(f"placing two ASK orders {size} @ {price},{price+1} with client_order_id={client_order_id},{client_order_id+1} on {product.name}...", end='', flush=True)
    maker.place_order(ctx, product, Side.ASK, size, price, client_order_id=client_order_id)
    maker.place_order(ctx, product, Side.ASK, size, price+1, client_order_id=client_order_id+1)
    print('success')

    taker_size = size*2
    print(f"taking both orders...", end='', flush=True)
    taker.place_order(ctx, product, Side.BID, taker_size, price+1)
    print('success')

    print('waiting a few seconds for the crank...', end='', flush=True)
    await asyncio.sleep(CRANK_SLEEP_SECONDS)
    print('checking open orders...', end='', flush=True)
    open_orders = list(maker.open_orders(ctx))
    if len(open_orders) != 0:
        print("printing open orders")
        for o in open_orders:
            print(o)
        raise RuntimeError(f"expected zero maker open orders but saw {len(open_orders)} open orders")
    open_orders = list(taker.open_orders(ctx))
    if len(open_orders) != 0:
        print("printing open orders")
        for o in open_orders:
            print(o)
        raise RuntimeError(f"expected zero taker open orders but saw {len(open_orders)} open orders")
    print('success')

    client_order_id = int(random() * 1e6)
    print(f"placing ASK order {size} @ {price} with client_order_id={client_order_id} on {product.name}...", end='', flush=True)
    maker.place_order(ctx, product, Side.ASK, size, price, client_order_id=client_order_id)
    print('success')

    taker_size = size*0.25
    print(f"taking {size} @ {price}...", end='', flush=True)
    taker.place_order(ctx, product, Side.BID, taker_size, price)
    print('success')
    
    print('waiting a few seconds for the crank...', end='', flush=True)
    await asyncio.sleep(CRANK_SLEEP_SECONDS)
    print('done waiting')
    print('checking open orders...', end='', flush=True)
    open_orders = list(maker.open_orders(ctx))
    if len(open_orders) != 1:
        print("printing open orders")
        for o in open_orders:
            print(o)
        raise RuntimeError(f"expected 1 open order but saw {len(open_orders)} open orders")
    if open_orders[0].client_order_id != client_order_id:
        print("printing open orders")
        for o in open_orders:
            print(o)
        raise RuntimeError(f"expected 1 open order but saw {len(open_orders)} open orders")
    if round(open_orders[0].qty, 3) != round(size*0.75, 3):
        print("printing open orders")
        for o in open_orders:
            print(o)
        raise RuntimeError(f"expected open_orders[0].qty = {round(size*0.75, 3)} but saw {round(open_orders[0].qty, 3)}")
    print('success')

    taker_size = size*0.25
    print(f"taking {size} @ {price}...", end='', flush=True)
    taker.place_order(ctx, product, Side.BID, taker_size, price)
    print('success')
    
    print('waiting a few seconds for the crank...', end='', flush=True)
    await asyncio.sleep(CRANK_SLEEP_SECONDS)
    print('done waiting')
    print('checking open orders...', end='', flush=True)
    open_orders = list(maker.open_orders(ctx))
    if len(open_orders) != 1:
        print("printing open orders")
        for o in open_orders:
            print(o)
        raise RuntimeError(f"expected 1 open order but saw {len(open_orders)} open orders")
    if open_orders[0].client_order_id != client_order_id:
        print("printing open orders")
        for o in open_orders:
            print(o)
        raise RuntimeError(f"expected 1 open order but saw {len(open_orders)} open orders")
    if round(open_orders[0].qty, 3) != round(size*0.5, 3):
        print("printing open orders")
        for o in open_orders:
            print(o)
        raise RuntimeError(f"expected open_orders[0].qty = {round(size*0.5, 3)} but saw {round(open_orders[0].qty, 3)}")
    print('success')


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
