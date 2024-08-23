import json
from random import random
import sys
import time

print('importing dexterity (it takes a while)...', end='', flush=True)
from dexteritysdk.dex.sdk_context import SDKContext, SDKTrader, MultiplaceOrder
from dexteritysdk.utils.aob import Side
print('success')
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey


CRANK_SLEEP_SECONDS = 5 # 0.400 * 31 # 400 ms per slot times 31 slots for confirmed
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

    print('creating new trg...', end='', flush=True)
    trader = ctx.register_trader(keypair)
    print('success (trg pubkey: {})'.format(trader.account))
    print('subscribing...', end='', flush=True)
    asyncio.create_task(trader.subscribe(ctx, 'ws://localhost:8900'))
    await asyncio.sleep(1)
    print('success')

    print('depositing 100k USDC...', end='', flush=True)
    trader.deposit(ctx, 100000)
    print('success')

    print('withdrawing 1k USDC...', end='', flush=True)
    trader.withdraw(ctx, 1000)
    print('success')

    print('checking balance...', end='', flush=True)
    trg, _ = trader.get_trader_risk_group()
    trg.cash_balance
    print('success... (cash balance: {})'.format(trg.cash_balance))

    print('checking balance...', end='', flush=True)
    trg, _ = trader.get_trader_risk_group()
    trg.cash_balance
    print('success... (cash balance: {})'.format(trg.cash_balance))

    print('checking mark prices')
    for product in ctx.products:
        mark_price = ctx.get_mark_price(product.key)
        index_price = ctx.get_index_price(product.key)
        oracle_minus_book_ewma = ctx.get_oracle_minus_book_ewma(product.key)
        print(f"{product.name}: mark: {mark_price}, index: {index_price}, spread ema: {oracle_minus_book_ewma}")

    tick = 0.1
    size = tick

    print('checking open orders...', end='', flush=True)
    open_orders = list(trader.open_orders(ctx))
    if len(open_orders) != 0:
        print("printing open orders")
        for o in open_orders:
            print(o)
        raise RuntimeError(f"expected zero open orders but saw but saw {len(open_orders)} open orders")
    print('success')

    for product in ctx.products:
        if 'BTC' in product.name:
            price = BTC_PRICE
            size = 0.1
        elif 'ETH' in product.name:
            price = ETH_PRICE
            size = 0.1
        elif 'SOL' in product.name:
            price = SOL_PRICE
            size = 0.1
        elif 'BITCOIN' in product.name:
            price = 0.06
            size = 1
        elif 'OPOS' in product.name:
            price = 6
            size = 1
        print(f"multiplacing orders on {product.name}...", end='', flush=True)
        # TODO: actually figure out how to return a List[OrderSummary] from trader.multiplace
        order_summaries = trader.multiplace(ctx, product, [
            MultiplaceOrder(
                side=Side.ASK,
                size=size,
                price=price,
                client_order_id=0,
            ),
            MultiplaceOrder(
                side=Side.BID,
                size=size,
                price=price,
                client_order_id=1,
            ),
        ])
        print(order_summaries)
        print('success')

        # once the following TODO is done, we can run this code:
        # TODO: actually figure out how to return a List[OrderSummary] from trader.multiplace
        # print(f"replacing order on {product.name}...", end='', flush=True)
        # order_summary = trader.replace(
        #     ctx,
        #     product,
        #     order_summary.order_id,
        #     Side.ASK,
        #     size,
        #     price,
        # )
        # print('success')
        # 
        # print(f"cancelling order on {product.name}...", end='', flush=True)
        # trader.cancel(ctx, product, order_summary.order_id)
        # print('success')
    print('success')

    print('waiting a few seconds for the crank...', end='', flush=True)
    await asyncio.sleep(CRANK_SLEEP_SECONDS)
    print('done waiting')

    batch_size=2
    print(f"calling cancel_all_orders...", end='', flush=True)
    trader.cancel_all_orders(ctx)
    print('success')

    print('waiting a few seconds for the crank...', end='', flush=True)
    await asyncio.sleep(CRANK_SLEEP_SECONDS)
    print('done waiting')

    print('checking open orders...', end='', flush=True)
    open_orders = list(trader.open_orders(ctx))
    if len(open_orders) != 0:
        print("printing open orders")
        for o in open_orders:
            print(o)
        raise RuntimeError(f"expected zero open orders but saw but saw {len(open_orders)} open orders")
    print('success')

    for product in ctx.products:
        if 'BTC' in product.name:
            price = BTC_PRICE
            size = 0.1
        elif 'ETH' in product.name:
            price = ETH_PRICE
            size = 0.1
        elif 'SOL' in product.name:
            price = SOL_PRICE
            size = 0.1
        elif 'BITCOIN' in product.name:
            price = 0.06
            size = 1
        elif 'OPOS' in product.name:
            price = 6
            size = 1
        client_order_id = int(random() * 1e6)
        print(f"placing order with client_order_id={client_order_id} on {product.name}...", end='', flush=True)
        trader.place_order(ctx, product, Side.ASK, size, price, client_order_id=client_order_id)
        print('success')

        print('checking open orders...', end='', flush=True)
        open_orders = list(trader.open_orders(ctx))
        if len(open_orders) != 1:
            print("printing open orders")
            for o in open_orders:
                print(o)
            raise RuntimeError(f"expected 1 open order but saw {len(open_orders)} open orders")
        if open_orders[0].client_order_id != client_order_id:
            print("printing open orders")
            for o in open_orders:
                print(o)
            raise RuntimeError(f"expected open_orders[0].client_order_id = {client_order_id} but saw {open_orders[0].client_order_id}")
        print('success')

        print(f"cancelling order with client_order_id={client_order_id} on {product.name}...", end='', flush=True)
        trader.cancel(ctx, product, 0, client_order_id=client_order_id)
        print('success')

        print('waiting a few seconds for the crank...', end='', flush=True)
        await asyncio.sleep(CRANK_SLEEP_SECONDS)
        print('done waiting')
        print('checking open orders...', end='', flush=True)
        open_orders = list(trader.open_orders(ctx))
        if len(open_orders) != 0:
            print("printing open orders")
            for o in open_orders:
                print(o)
            raise RuntimeError(f"expected zero open orders but saw but saw {len(open_orders)} open orders")
        print('success')

    print('success')

    print('waiting a few seconds for the crank...', end='', flush=True)
    await asyncio.sleep(CRANK_SLEEP_SECONDS)
    print('done waiting')
    print('checking open orders...', end='', flush=True)
    open_orders = list(trader.open_orders(ctx))
    if len(open_orders) != 0:
        print("printing open orders")
        for o in open_orders:
            print(o)
        raise RuntimeError(f"expected zero open orders but saw but saw {len(open_orders)} open orders")
    print('success')

    for product in ctx.products:
        if 'BTC' in product.name:
            price = BTC_PRICE
            size = 0.1
        elif 'ETH' in product.name:
            price = ETH_PRICE
            size = 0.1
        elif 'SOL' in product.name:
            price = SOL_PRICE
            size = 0.1
        elif 'BITCOIN' in product.name:
            price = 0.06
            size = 1
        elif 'OPOS' in product.name:
            price = 6
            size = 1
        print(f"placing order on {product.name}...", end='', flush=True)
        order_summary = trader.place_order(ctx, product, Side.ASK, size, price)
        print('success')

    batch_size = 1
    print(f"calling cancel_all_orders...", end='', flush=True)
    trader.cancel_all_orders(ctx)
    print('success')

    batch_size = 2
    for product in ctx.products:
        if 'BTC' in product.name:
            price = BTC_PRICE
            size = 0.1
        elif 'ETH' in product.name:
            price = ETH_PRICE
            size = 0.1
        elif 'SOL' in product.name:
            price = SOL_PRICE
            size = 0.1
        elif 'BITCOIN' in product.name:
            price = 0.06
            size = 1
        elif 'OPOS' in product.name:
            price = 6
            size = 1
        for i in range(batch_size):
            print(f"placing order on {product.name}...", end='', flush=True)
            order_summary = trader.place_order(ctx, product, Side.ASK, size + i*tick, price)
            print('success')

    print(f"calling cancel_all_orders...", end='', flush=True)
    trader.cancel_all_orders(ctx)
    print('success')

    batch_size = 4
    for product in ctx.products:
        if 'BTC' in product.name:
            price = BTC_PRICE
            size = 0.1
        elif 'ETH' in product.name:
            price = ETH_PRICE
            size = 0.1
        elif 'SOL' in product.name:
            price = SOL_PRICE
            size = 0.1
        elif 'BITCOIN' in product.name:
            price = 0.06
            size = 1
        elif 'OPOS' in product.name:
            price = 6
            size = 1
        for i in range(batch_size):
            print(f"placing order on {product.name}...", end='', flush=True)
            order_summary = trader.place_order(ctx, product, Side.ASK, size + i*tick, price)
            print('success')

    print(f"calling cancel_all_orders...", end='', flush=True)
    trader.cancel_all_orders(ctx)
    print('success')

    batch_size = 8
    for product in ctx.products:
        if 'BTC' in product.name:
            price = BTC_PRICE
            size = 0.1
        elif 'ETH' in product.name:
            price = ETH_PRICE
            size = 0.1
        elif 'SOL' in product.name:
            price = SOL_PRICE
            size = 0.1
        elif 'BITCOIN' in product.name:
            price = 0.06
            size = 1
        elif 'OPOS' in product.name:
            price = 6
            size = 1
        for i in range(batch_size):
            print(f"placing order on {product.name}...", end='', flush=True)
            order_summary = trader.place_order(ctx, product, Side.ASK, size + i*tick, price)
            print('success')

    print(f"calling cancel_all_orders...", end='', flush=True)
    trader.cancel_all_orders(ctx)
    print('success')

    for product in ctx.products:
        if 'BTC' in product.name:
            price = BTC_PRICE
            size = 0.1
        elif 'ETH' in product.name:
            price = ETH_PRICE
            size = 0.1
        elif 'SOL' in product.name:
            price = SOL_PRICE
            size = 0.1
        elif 'BITCOIN' in product.name:
            price = 0.06
            size = 1
        elif 'OPOS' in product.name:
            price = 6
            size = 1
        print(f"placing order on {product.name}...", end='', flush=True)
        order_summary = trader.place_order(ctx, product, Side.ASK, size, price)
        print('success')

        print(f"replacing order on {product.name}...", end='', flush=True)
        order_summary = trader.replace(
            ctx,
            product,
            order_summary.order_id,
            Side.ASK,
            size,
            price,
        )
        print('success')

        print(f"cancelling order on {product.name}...", end='', flush=True)
        trader.cancel(ctx, product, order_summary.order_id)
        print('success')
    print('success')

    print('waiting a few seconds for the crank...', end='', flush=True)
    await asyncio.sleep(CRANK_SLEEP_SECONDS)
    print('done waiting')
    print('checking open orders...', end='', flush=True)
    open_orders = list(trader.open_orders(ctx))
    if len(open_orders) != 0:
        print("printing open orders")
        for o in open_orders:
            print(o)
        raise RuntimeError(f"expected zero open orders but saw but saw {len(open_orders)} open orders")
    print('success')

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
