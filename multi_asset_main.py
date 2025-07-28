# multi_asset_main.py

from bybit_feed import BybitFeed
from cvd_engine import CVDEngine
from cvd_multi_tf_engine import MultiTimeframeCVDEngine
from multi_tf_divergence_matrix import detect_multi_tf_divergence_matrix
from cvd_ai_score import score_cvd_signal_from_matrix
from cvd_memory_store import CVDMemoryStore
from discord_notifier import send_discord_alert
import asyncio

WATCH_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
MAX_HISTORY = 30

# 🔧 Used to prevent multiple test alerts
test_alert_sent = {}

async def start_sniper(symbol):
    print(f"🚀 Starting sniper loop for {symbol}")

    cvd = CVDEngine()
    multi_cvd = MultiTimeframeCVDEngine()
    memory = CVDMemoryStore()
    price_history = []
    test_alert_sent[symbol] = False

    async def on_tick(data):
        # Update CVD engines
        cvd_value = cvd.update(data["buy_volume"], data["sell_volume"], data["timestamp"])
        multi_cvd.update(data["buy_volume"], data["sell_volume"], data["timestamp"])

        # Maintain price history
        price_history.append(data["price"])
        if len(price_history) > MAX_HISTORY:
            price_history.pop(0)

        price_data_map = {
            "1m": price_history,
            "3m": price_history,
            "5m": price_history,
            "15m": price_history
        }

        # Run divergence detection
        divergence_matrix = detect_multi_tf_divergence_matrix(price_data_map, multi_cvd, lookback=5)
        print(f"[{symbol}] 📊 Matrix: {divergence_matrix}")

        vwap_relation = "failing reclaim"
        delta_behavior = "spike_no_follow"

        result = score_cvd_signal_from_matrix(divergence_matrix, vwap_relation, delta_behavior)

        # 🧪 Force test alert (BTC only, once)
        if symbol == "BTCUSDT" and not test_alert_sent[symbol]:
            result["score"] = 95
            result["setup"] = "sniper trap (TEST)"
            result["reasons"] = ["FORCED TEST divergence", "fake VWAP reclaim", "delta spike"]
            print(f"🚨 [TEST MODE] Sending forced sniper alert for {symbol}")
            send_discord_alert(symbol, result, data["price"], divergence_matrix)
            test_alert_sent[symbol] = True
            return

        # Regular live alert (score must be high)
        if result["score"] > 60:
            print(f"🚨 SNIPER TRAP [{symbol}] | Score: {result['score']}")
            memory.log_event(data["timestamp"], cvd_value, data["price"], divergence_matrix, result["score"])
            send_discord_alert(symbol, result, data["price"], divergence_matrix)
        else:
            print(f"[{symbol}] ↪ No trap | Score: {result['score']}")

    feed = BybitFeed(symbol=symbol)
    await feed.connect(on_tick)

async def main():
    await asyncio.gather(*[start_sniper(symbol) for symbol in WATCH_SYMBOLS])

if __name__ == "__main__":
    asyncio.run(main())
