# main.py

from bybit_feed import BybitFeed
from cvd_engine import CVDEngine
from cvd_multi_tf_engine import MultiTimeframeCVDEngine
from cvd_divergence_detector import detect_cvd_divergence
from multi_tf_divergence_matrix import check_multi_tf_divergence
from cvd_ai_score import score_cvd_signal
from cvd_memory_store import CVDMemoryStore
from discord_notifier import send_discord_alert
import asyncio

# Initialize engines
cvd = CVDEngine()
multi_cvd = MultiTimeframeCVDEngine()
memory = CVDMemoryStore()

price_history = []  # 1m price history
MAX_HISTORY = 20    # for up to 15m divergence check

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

    # Update price history (1m resolution for now)
    price_history.append(data["price"])
    if len(price_history) > MAX_HISTORY:
        price_history.pop(0)

    # Pull CVD series for each timeframe
    cvd_data_map = {
        "1m": multi_cvd.get_cvd_series("1m"),
        "3m": multi_cvd.get_cvd_series("3m"),
        "5m": multi_cvd.get_cvd_series("5m"),
        "15m": multi_cvd.get_cvd_series("15m"),
    }

    price_data_map = {
        "1m": price_history,
        "3m": price_history,   # Placeholder for now
        "5m": price_history,   # Replace with real TF candles
        "15m": price_history   # Same here
    }

    # Get divergence per timeframe
    divergence_matrix = check_multi_tf_divergence(price_data_map, cvd_data_map, lookback=5)
    print("📊 CVD Divergence Matrix:", divergence_matrix)

    # Use 1m divergence to score sniper setup (multi-TF scoring next)
    divergence = {"divergence": divergence_matrix["1m"]} if divergence_matrix["1m"] in ["bullish", "bearish"] else None
    vwap_relation = "failing reclaim"        # Placeholder
    delta_behavior = "spike_no_follow"       # Placeholder

    result = score_cvd_signal(divergence, vwap_relation, delta_behavior)

    if result["score"] > 60:
        memory.log_event(data["timestamp"], cvd_value, data["price"], divergence, result["score"])
        msg = f"""
🎯 **LIVE SNIPER TRAP DETECTED**
**Score:** {result['score']}
**Setup:** {result['setup']}
**Price:** {data['price']}
**1m Divergence:** {divergence_matrix['1m']}
**Reasons:**
- {'\n- '.join(result['reasons'])}
"""
        print(msg)
        send_discord_alert(msg)
    else:
        print(f"↪ No sniper trap | 1m divergence: {divergence_matrix['1m']} | Score: {result['score']}")

async def main():
    feed = BybitFeed()
    await feed.connect(on_tick)

if __name__ == "__main__":
    asyncio.run(main())
