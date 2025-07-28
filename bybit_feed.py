# bybit_feed.py

import asyncio
import websockets
import json
import time

class BybitFeed:
    def __init__(self, symbol="BTCUSDT", interval=1):
        self.symbol = symbol.upper()
        self.interval = interval  # seconds between emissions
        self.buy_volume = 0.0
        self.sell_volume = 0.0
        self.price = 0.0
        self.last_emit_time = time.time()

    async def connect(self, on_tick):
        url = "wss://stream.bybit.com/v5/public/linear"

        async with websockets.connect(url) as ws:
            subscribe_msg = {
                "op": "subscribe",
                "args": [f"publicTrade.{self.symbol}"]
            }
            await ws.send(json.dumps(subscribe_msg))
            print(f"✅ Connected to Bybit feed: {self.symbol}")

            async for message in ws:
                try:
                    data = json.loads(message)
                    trades = data.get("data", [])
                    for trade in trades:
                        price = float(trade["p"])
                        volume = float(trade["v"])
                        side = trade["S"]

                        if side == "Buy":
                            self.buy_volume += volume
                        else:
                            self.sell_volume += volume

                        self.price = price

                    # Emit on interval (approx)
                    now = time.time()
                    if now - self.last_emit_time >= self.interval:
                        await on_tick({
                            "buy_volume": self.buy_volume,
                            "sell_volume": self.sell_volume,
                            "price": self.price,
                            "timestamp": now
                        })
                        self.buy_volume = 0.0
                        self.sell_volume = 0.0
                        self.last_emit_time = now

                except Exception as e:
                    print(f"❌ Error in {self.symbol} feed: {e}")
