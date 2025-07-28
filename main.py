# main.py

from bybit_feed import BybitFeed
from cvd_engine import CVDEngine
from cvd_multi_tf_engine import MultiTimeframeCVDEngine
from cvd_divergence_detector import detect_cvd_divergence
from cvd_ai_score import score_cvd_signal
from cvd_memory_store import CVDMemoryStore
from discord_notifier import send_discord_alert
import asyncio

# Initialize engines
cvd = CVDEngine()
multi_cvd = MultiTimeframeCVDEngine()
memory = CVDMemoryStore()

price_history = []
cvd_history_1m = []

async def on_tick(data):
    # Update global CVD
    cvd_value = cvd.update(
        buy_volume=data["buy_volume"],
        sell_volume=data["sell_volume"],
        timestamp=data["timestamp"]
    )

    # Update multi-timeframe CVD
    multi_cvd.update(
        buy_volume=data["buy_volume"],
        sell_volume=data["sell_volume"],
        timestamp=data["timestamp"]
    )

    # Maintain price and 1m CVD history
    price_history.append(data["price"])
    if len(price_history) > 10:
        price_history.pop(0)

    cvd_history_1m = multi_cvd.get_cvd_series("1m")
    if len(cvd_history_1m) < 6 or len(price_history) < 6:
        return  # not enough data to check divergence yet

    # Detect divergence (on 1m only for now)
    divergence = detect_cvd_divergence(price_history[-6:], cvd_history_1m[-6:])
    vwap_relation = "failing reclaim"  # placeholder for future VWAP module
    delta_behavior = "spike_no_follow"  # placeholder for future delta logic

    result = score_cvd_signal(divergence, vwap_relation, delta_behavior)

    if result["score"] > 60:
        memory.log_event(data["timestamp"], cvd_value, data["price"], divergence, result["score"])
        msg = f"""
🎯 **LIVE SNIPER TRAP DETECTED**
**Score:** {result['score']}
**Setup:** {result['setup']}
**Price:** {data['price']}
**Reasons:**
- {'\n- '.join(result['reasons'])}
"""
        print(msg)
        send_discord_alert(msg)
    else:
        print(f"↪ No valid sniper signal | Score: {result['score']}")

async def main():
    feed = BybitFeed()
    await feed.connect(on_tick)

if __name__ == "__main__":
    asyncio.run(main())
