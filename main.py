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
from vwap_engine import VWAPEngine
import asyncio

SYMBOL = "BTCUSDT"
MAX_HISTORY = 30
ACTIVE_TFS = ["1m", "3m", "5m", "15m", "30m", "1h"]

cvd = CVDEngine()
multi_cvd = MultiTimeframeCVDEngine()
memory = CVDMemoryStore()
vwap_engine = VWAPEngine()
price_history = []

async def on_tick(data):
    # Update core engines
    cvd_value = cvd.update(data["buy_volume"], data["sell_volume"], data["timestamp"])
    multi_cvd.update(data["buy_volume"], data["sell_volume"], data["timestamp"])
    vwap = vwap_engine.update(data["price"], data["buy_volume"] + data["sell_volume"])
    vwap_status = vwap_engine.get_relation(data["price"])

    # Maintain price history
    price_history.append(data["price"])
    if len(price_history) > MAX_HISTORY:
        price_history.pop(0)

    # Timeframe-based data map
    price_data_map = {tf: price_history for tf in ACTIVE_TFS}
    divergence_matrix = detect_multi_tf_divergence_matrix(price_data_map, multi_cvd, lookback=5)
    print(f"[{SYMBOL}] 📊 CVD Matrix:\n{divergence_matrix}")
    print(f"[{SYMBOL}] 📍 VWAP: {vwap:.2f} | Status: {vwap_status}")

    # AI CVD reader on key timeframes
    for tf in ACTIVE_TFS:
        price_series = price_history[-6:]
        cvd_series = multi_cvd.get_cvd_series(tf)[-6:]
        insight = ai_cvd_reader(price_series, cvd_series, timeframe=tf)
        if insight["confidence"] >= 80:
            print(f"🧠 Insight [{tf}]: {insight['trap_type']} | Confidence: {insight['confidence']}")

    # Scoring with VWAP logic included
    delta_behavior = "spike_no_follow"
    result = score_cvd_signal_from_matrix(divergence_matrix, vwap_status, delta_behavior)

    # Trigger sniper trap alert
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
        print(f"✅ {tf} CVD loaded ({len(cvd_mem[tf])} points)")

    print(f"🚀 Starting sniper engine for {SYMBOL}")
    feed = BybitFeed(symbol=SYMBOL)
    await feed.connect(on_tick)

if __name__ == "__main__":
    asyncio.run(main())
