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
from htf_vwap_engine import HTFVWAPEngine
from bias_engine import detect_htf_bias
import asyncio

SYMBOL = "BTCUSDT"
MAX_HISTORY = 30
ACTIVE_TFS = ["1m", "3m", "5m", "15m", "30m", "1h", "4h"]

cvd = CVDEngine()
multi_cvd = MultiTimeframeCVDEngine()
memory = CVDMemoryStore()
vwap_engine = VWAPEngine()
htf_vwap = HTFVWAPEngine()
price_history = []

async def on_tick(data):
    # --- Engine Updates ---
    cvd_value = cvd.update(data["buy_volume"], data["sell_volume"], data["timestamp"])
    multi_cvd.update(data["buy_volume"], data["sell_volume"], data["timestamp"])
    session_vwap = vwap_engine.update(data["price"], data["buy_volume"] + data["sell_volume"])
    vwap_status = vwap_engine.get_relation(data["price"])
    htf_vwap.update(data["price"], data["buy_volume"] + data["sell_volume"], data["timestamp"])
    weekly_status = htf_vwap.get_relation("weekly", data["price"])
    monthly_status = htf_vwap.get_relation("monthly", data["price"])

    # --- Price History ---
    price_history.append(data["price"])
    if len(price_history) > MAX_HISTORY:
        price_history.pop(0)

    # --- CVD Matrix + Trap Insights ---
    price_data_map = {tf: price_history for tf in ACTIVE_TFS}
    divergence_matrix = detect_multi_tf_divergence_matrix(price_data_map, multi_cvd, lookback=5)
    print(f"[{SYMBOL}] 📊 CVD Matrix:\n{divergence_matrix}")
    print(f"[{SYMBOL}] 📍 VWAP: {session_vwap:.2f} | Weekly: {weekly_status} | Monthly: {monthly_status}")

    trap_insights = []
    for tf in ACTIVE_TFS:
        cvd_series = multi_cvd.get_cvd_series(tf)[-6:]
        price_series = price_history[-6:]
        insight = ai_cvd_reader(price_series, cvd_series, tf)
        if insight["confidence"] >= 80:
            trap_insights.append({
                "tf": tf,
                "trap_type": insight["trap_type"],
                "confidence": insight["confidence"]
            })
            print(f"🧠 [{tf}] Trap: {insight['trap_type']} | Conf: {insight['confidence']}")

    # --- HTF Bias Detection (using 4h) ---
    bias = detect_htf_bias(
        price_series=price_history[-6:],
        cvd_series=multi_cvd.get_cvd_series("4h")[-6:],
        vwaps={"weekly": weekly_status, "monthly": monthly_status}
    )
    print(f"🧠 HTF Bias: {bias['htf_bias']} | Structure: {bias['structure']} | Trap focus: {bias['preferred_trap']}")

    # --- Scoring + Filter ---
    delta_behavior = "spike_no_follow"
    result = score_cvd_signal_from_matrix(divergence_matrix, vwap_status, delta_behavior)

    # --- Alert & Log ---
    if result["score"] > 60 and should_alert(SYMBOL, data["price"], divergence_matrix):
        print(f"🚨 SNIPER TRAP [{SYMBOL}] | Score: {result['score']}")
        memory.log_event(data["timestamp"], cvd_value, data["price"], divergence_matrix, result["score"])
        send_discord_alert(
            SYMBOL,
            result,
            data["price"],
            divergence_matrix,
            vwap_status,
            trap_insights
        )
    else:
        print(f"[{SYMBOL}] ↪ No trap | Score: {result['score']}")

# --- Launch + Backfill ---
async def main():
    print(f"🧠 Backfilling CVD memory for {SYMBOL}")
    price_mem, cvd_mem = backfill_cvd(SYMBOL)

    for tf in cvd_mem:
        multi_cvd.cvd_history[tf] = cvd_mem[tf]
        if tf == "1m":
            price_history.extend(price_mem[tf][-MAX_HISTORY:])
        print(f"✅ {tf} CVD loaded ({len(cvd_mem[tf])} pts)")

    print(f"🚀 Starting sniper engine for {SYMBOL}")
    feed = BybitFeed(symbol=SYMBOL)
    await feed.connect(on_tick)

if __name__ == "__main__":
    asyncio.run(main())
