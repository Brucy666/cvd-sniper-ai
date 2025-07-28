# main.py

from bybit_feed import BybitFeed
from cvd_engine import CVDEngine
from cvd_multi_tf_engine import MultiTimeframeCVDEngine
from multi_tf_divergence_matrix import detect_multi_tf_divergence_matrix
from cvd_ai_score import score_cvd_signal_from_matrix
from cvd_memory_store import CVDMemoryStore
from discord_notifier import send_discord_alert
from cvd_backfill import backfill_cvd
from trap_cooldown import should_alert
from ai_cvd_reader import ai_cvd_reader
import asyncio

SYMBOL = "BTCUSDT"
MAX_HISTORY = 30

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

    # Updated with 30m + 1h
    price_data_map = {
        "1m": price_history,
        "3m": price_history,
        "5m": price_history,
        "15m": price_history,
        "30m": price_history,
        "1h": price_history
    }

    divergence_matrix = detect_multi_tf_divergence_matrix(price_data_map, multi_cvd, lookback=5)
    print(f"[{SYMBOL}] 📊 CVD Matrix: {divergence_matrix}")

    cvd_series_1m = multi_cvd.get_cvd_series("1m")[-6:]
    price_series_1m = price_history[-6:]
    cvd_insight = ai_cvd_reader(price_series_1m, cvd_series_1m)
    print(f"[{SYMBOL}] 🧠 AI Insight: {cvd_insight}")

    vwap_relation = "failing reclaim"
    delta_behavior = "spike_no_follow"
    result = score_cvd_signal_from_matrix(divergence_matrix, vwap_relation, delta_behavior)

    if result["score"] > 60 and should_alert(SYMBOL, data["price"], divergence_matrix):
        print(f"🚨 SNIPER TRAP [{SYMBOL}] | Score: {result['score']}")
        memory.log_event(data["timestamp"], cvd_value, data["price"], divergence_matrix, result["score"])
        send_discord_alert(SYMBOL, result, data["price"], divergence_matrix)
    else:
        print(f"[{SYMBOL}] ↪ No trap | Score: {result['score']}")

async def main():
    print(f"🧠 Backfilling CVD memory for {SYMBOL}")
    price_mem, cvd_mem = backfill_cvd(SYMBOL)

    for tf in cvd_mem:
        multi_cvd.cvd_history[tf] = cvd_mem[tf]
        if tf == "1m":
            price_history.extend(price_mem[tf][-MAX_HISTORY:])
        print(f"✅ {tf} CVD loaded ({len(cvd_mem[tf])} pts)")

    print(f"🚀 Starting sniper feed for {SYMBOL}")
    feed = BybitFeed(symbol=SYMBOL)
    await feed.connect(on_tick)

if __name__ == "__main__":
    asyncio.run(main())
