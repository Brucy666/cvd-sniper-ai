# bybit_feed.py

import asyncio
import websockets
import json
import time

class BybitFeed:
    def __init__(self, symbol="BTCUSDT", interval=1):
        self.symbol = symbol
        self.interval = interval  # time window to group volume (in seconds)
        self.buy_volume = 0.0
        self.sell_volume = 0.0
        self.price = 0.0

    async def connect(self, on_tick):
        url = "wss://stream.bybit.com/v5/public/linear"

        async with websockets.connect(url) as ws:
            await ws.send(json.dumps({
                "op": "subscribe",
                "args": [f"publicTrade.{self.symbol}"]
            }))
            print("✅ Connected to Bybit feed")

            async for message in ws:
                try:
                    data = json.loads(message)
                    trades = data.get("data", [])
                    for trade in trades:
                        price = float(trade["p"])
                        volume = float(trade["v"])
                        side = trade["S"]  # Buy or Sell

                        if side == "Buy":
                            self.buy_volume += volume
                        else:
                            self.sell_volume += volume
                        
                        self.price = price

                    # Emit data once per interval
                    if time.time() % self.interval < 0.1:
                        await on_tick({
                            "buy_volume": self.buy_volume,
                            "sell_volume": self.sell_volume,
                            "price": self.price,
                            "timestamp": time.time()
                        })
                        self.buy_volume = 0.0
                        self.sell_volume = 0.0

                except Exception as e:
                    print(f"❌ Feed error: {e}")
