# multi_asset_main.py

from bybit_feed import BybitFeed
from cvd_engine import CVDEngine
from cvd_multi_tf_engine import MultiTimeframeCVDEngine
from multi_tf_divergence_matrix import detect_multi_tf_divergence_matrix
from cvd_ai_score import score_cvd_signal_from_matrix
from cvd_memory_store import CVDMemoryStore
from discord_notifier import send_discord_alert
import asyncio

MAX_HISTORY = 30
WATCH_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]  # You can expand this list

async def start_sniper(symbol):
    print(f"🚀 Starting sniper engine for {symbol}")

    cvd = CVDEngine()
    multi_cvd = MultiTimeframeCVDEngine()
    memory = CVDMemoryStore()
    price_history = []

    async def on_tick(data):
        cvd_value = cvd.update(data["buy_volume"], data["sell_volume"], data["timestamp"])
        multi_cvd.update(data["buy_volume"], data["sell_volume"], data["timestamp"])

        price_history.append(data["price"])
        if len(price_history) > MAX_HISTORY:
            price_history.pop(0)

        price_data_map = {
            "1m": price_history,
            "3m": price_history,
            "5m": price_history,
            "15m": price_history,
        }

        divergence_matrix = detect_multi_tf_divergence_matrix(price_data_map, multi_cvd, lookback=5)
        print(f"[{symbol}] 📊 Matrix:", divergence_matrix)

        vwap_relation = "failing reclaim"
        delta_behavior = "spike_no_follow"

        result = score_cvd_signal_from_matrix(divergence_matrix, vwap_relation, delta_behavior)

        if result["score"] > 60:
            memory.log_event(data["timestamp"], cvd_value, data["price"], divergence_matrix, result["score"])
            msg = f"""
🎯 **SNIPER TRAP: {symbol}**
**Score:** {result['score']}
**Setup:** {result['setup']}
**Price:** {data['price']}
**CVD Divergence:** {divergence_matrix}
**Reasons:**
- {'\n- '.join(result['reasons'])}
"""
            print(msg)
            send_discord_alert(msg)
        else:
            print(f"[{symbol}] ↪ No sniper | Score: {result['score']}")

    feed = BybitFeed(symbol=symbol)
    await feed.connect(on_tick)

async def main():
    await asyncio.gather(*[start_sniper(symbol) for symbol in WATCH_SYMBOLS])

if __name__ == "__main__":
    asyncio.run(main())
