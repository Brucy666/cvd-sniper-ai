# main.py

from bybit_feed import BybitFeed
from cvd_engine import CVDEngine
from cvd_multi_tf_engine import MultiTimeframeCVDEngine
from multi_tf_divergence_matrix import check_multi_tf_divergence_matrix
from cvd_ai_score import score_cvd_signal_from_matrix
from cvd_memory_store import CVDMemoryStore
from discord_notifier import send_discord_alert
import asyncio

# Initialize modules
cvd = CVDEngine()
multi_cvd = MultiTimeframeCVDEngine()
memory = CVDMemoryStore()

price_history = []
MAX_HISTORY = 20  # for 15m coverage

async def on_tick(data):
    # Update cumulative volume delta
    cvd_value = cvd.update(data["buy_volume"], data["sell_volume"], data["timestamp"])
    multi_cvd.update(data["buy_volume"], data["sell_volume"], data["timestamp"])

    # Maintain recent price history
    price_history.append(data["price"])
    if len(price_history) > MAX_HISTORY:
        price_history.pop(0)

    # Get rolling CVD series per timeframe
    cvd_data_map = {
        "1m": multi_cvd.get_cvd_series("1m"),
        "3m": multi_cvd.get_cvd_series("3m"),
        "5m": multi_cvd.get_cvd_series("5m"),
        "15m": multi_cvd.get_cvd_series("15m"),
    }

    # For now, use same price series across TFs (can be replaced with real TF buckets later)
    price_data_map = {
        "1m": price_history,
        "3m": price_history,
        "5m": price_history,
        "15m": price_history,
    }

    # Run divergence matrix detection
    divergence_matrix = check_multi_tf_divergence_matrix(price_data_map, cvd_data_map, lookback=5)
    print("📊 CVD Divergence Matrix:", divergence_matrix)

    # Placeholder logic for confluence
    vwap_relation = "failing reclaim"
    delta_behavior = "spike_no_follow"

    # Score sniper setup using full matrix
    result = score_cvd_signal_from_matrix(divergence_matrix, vwap_relation, delta_behavior)

    if result["score"] > 60:
        memory.log_event(data["timestamp"], cvd_value, data["price"], divergence_matrix, result["score"])

        msg = f"""
🎯 **LIVE SNIPER TRAP DETECTED**
**Score:** {result['score']}
**Setup:** {result['setup']}
**Price:** {data['price']}
**Divergence Matrix:** {divergence_matrix}
**Reasons:**
- {'\n- '.join(result['reasons'])}
"""
        print(msg)
        send_discord_alert(msg)
    else:
        print(f"↪ No sniper trap | Score: {result['score']} | Matrix: {divergence_matrix}")

async def main():
    feed = BybitFeed()
    await feed.connect(on_tick)

if __name__ == "__main__":
    asyncio.run(main())
