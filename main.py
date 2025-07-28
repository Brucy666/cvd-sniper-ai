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
    # 🔄 Update CVD engines with live data
    cvd_value = cvd.update(data["buy_volume"], data["sell_volume"], data["timestamp"])
    multi_cvd.update(data["buy_volume"], data["sell_volume"], data["timestamp"])

    # 📈 Maintain price history
    price_history.append(data["price"])
    if len(price_history) > MAX_HISTORY:
        price_history.pop(0)

    # 🧠 Run divergence detection
    price_data_map = {
        "1m": price_history,
        "3m": price_history,
        "5m": price_history,
        "15m": price_history,
        "30m": price_history,
        "1h": price_history
    }

    divergence_matrix = detect_multi_tf_divergence_matrix(price_data_map, multi_cvd, lookback=5)
    print(f"[{SYMBOL}] 📊 CVD Matrix:\n{divergence_matrix}")

    # 🧠 AI CVD Reader Insight (optional use)
    cvd_series_1m = multi_cvd.get_cvd_series("1m")[-6:]
    price_series_1m = price_history[-6:]
    insight = ai_cvd_reader(price_series_1m, cvd_series_1m)
    print(f"[{SYMBOL}] 🧠 Insight: {insight['trap_signal']} | Confidence: {insight['confidence_level']}")

    # 🧮 Score trap with placeholder VWAP/delta logic
    vwap_relation = "failing reclaim"
    delta_behavior = "spike_no_follow"
    result = score_cvd_signal_from_matrix(divergence_matrix, vwap_relation, delta_behavior)

    # ✅ Alert only if new + strong
    if result["score"] > 60 and should_alert(SYMBOL, data["price"], divergence_matrix):
        print(f"🚨 SNIPER TRAP [{SYMBOL}] | Score: {result['score']}")
        memory.log_event(data["timestamp"], cvd_value, data["price"], divergence_matrix, result["score"])
        send_discord_alert(SYMBOL, result, data["price"], divergence_matrix)
    else:
        print(f"[{SYMBOL}] ↪ No sniper trap | Score: {result['score']}")

async def main():
    print(f"🧠 Backfilling historical CVD for {SYMBOL}")
    price_mem, cvd_mem = backfill_cvd(SYMBOL)

    for tf in cvd_mem:
        multi_cvd.cvd_history[tf] = cvd_mem[tf]
        if tf == "1m":
            price_history.extend(price_mem[tf][-MAX_HISTORY:])
        print(f"✅ Loaded {tf} CVD history ({len(cvd_mem[tf])} points)")

    print(f"🚀 Starting sniper feed for {SYMBOL}")
    feed = BybitFeed(symbol=SYMBOL)
    await feed.connect(on_tick)

if __name__ == "__main__":
    asyncio.run(main())
