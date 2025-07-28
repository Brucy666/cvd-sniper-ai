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
from bias_engine import detect_multi_level_bias
from fib_trap_detector import detect_fib_trap
from trap_journal import log_full_trap
from trap_outcome_tracker import update_outcomes
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

fib_swing_low = 117200  # TODO: Replace with dynamic logic
fib_swing_high = 117900

async def on_tick(data):
    cvd_value = cvd.update(data["buy_volume"], data["sell_volume"], data["timestamp"])
    multi_cvd.update(data["buy_volume"], data["sell_volume"], data["timestamp"])
    session_vwap = vwap_engine.update(data["price"], data["buy_volume"] + data["sell_volume"])
    vwap_status = vwap_engine.get_relation(data["price"])
    htf_vwap.update(data["price"], data["buy_volume"] + data["sell_volume"], data["timestamp"])
    weekly_status = htf_vwap.get_relation("weekly", data["price"])
    monthly_status = htf_vwap.get_relation("monthly", data["price"])

    price_history.append(data["price"])
    if len(price_history) > MAX_HISTORY:
        price_history.pop(0)

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
            print(f"🧠 [{tf}] Trap: {insight['trap_type']} | Confidence: {insight['confidence']}")

    fib_result = detect_fib_trap(
        swing_low=fib_swing_low,
        swing_high=fib_swing_high,
        current_price=data["price"],
        cvd_series_3m=multi_cvd.get_cvd_series("3m")[-6:],
        vwap_relation=vwap_status
    )
    if fib_result["triggered"]:
        trap_insights.append({
            "tf": "3m",
            "trap_type": "1.41 fib extension trap",
            "confidence": fib_result["confidence"]
        })
        print(f"📐 Fib trap triggered: {fib_result['reason']}")

    bias_stack = detect_multi_level_bias(
        price_data_map=price_data_map,
        cvd_engine=multi_cvd,
        vwaps={"weekly": weekly_status, "monthly": monthly_status}
    )
    print(f"🧠 Bias Stack → Low: {bias_stack['low']['bias']} | Mid: {bias_stack['mid']['bias']} | High: {bias_stack['high']['bias']} | Alignment: {bias_stack['alignment']}")

    delta_behavior = "spike_no_follow"
    result = score_cvd_signal_from_matrix(divergence_matrix, vwap_status, delta_behavior)

    if result["score"] > 60 and should_alert(SYMBOL, data["price"], divergence_matrix):
        print(f"🚨 SNIPER TRAP [{SYMBOL}] | Score: {result['score']}")
        memory.log_event(data["timestamp"], cvd_value, data["price"], divergence_matrix, result["score"])

        send_discord_alert(
            SYMBOL,
            result,
            data["price"],
            divergence_matrix,
            vwap_status,
            trap_insights,
            bias_stack
        )

        log_full_trap(
            symbol=SYMBOL,
            price=data["price"],
            timestamp=data["timestamp"],
            divergence_matrix=divergence_matrix,
            trap_insights=trap_insights,
            vwap_status=vwap_status,
            fib_result=fib_result,
            bias_stack=bias_stack,
            alert_score=result["score"],
            alert_reasons=result["reasons"]
        )
    else:
        print(f"[{SYMBOL}] ↪ No trap | Score: {result['score']}")

    # Evaluate trap outcomes
    update_outcomes(current_price=data["price"], current_time=data["timestamp"])
    print("🔁 Checked trap outcomes for updates")


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
