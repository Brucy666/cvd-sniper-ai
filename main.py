# main.py

from bybit_feed import BybitFeed
from cvd_engine import CVDEngine
from cvd_multi_tf_engine import MultiTimeframeCVDEngine
from multi_tf_divergence_matrix import detect_multi_tf_divergence_matrix
from cvd_ai_score import score_cvd_signal_from_matrix
from cvd_memory_store import CVDMemoryStore
from discord_notifier import send_discord_alert
import asyncio

# Initialize engines
cvd = CVDEngine()
multi_cvd = MultiTimeframeCVDEngine()
memory = CVDMemoryStore()

# Price history buffer shared across timeframes (for now)
price_history = []
MAX_HISTORY = 30  # enough for up to 15m with lookback slices

async def on_tick(data):
    # Feed new trade into CVD engines
    cvd_value = cvd.update(data["buy_volume"], data["sell_volume"], data["timestamp"])
    multi_cvd.update(data["buy_volume"], data["sell_volume"], data["timestamp"])

    # Maintain price history
    price_history.append(data["price"])
    if len(price_history) > MAX_HISTORY:
        price_history.pop(0)

    # Price data map per timeframe (real TF bucketing coming later)
    price_data_map = {
        "1m": price_history,
        "3m": price_history,
        "5m": price_history,
        "15m": price_history
    }

    # Detect CVD divergence across all TFs
    divergence_matrix = detect_multi_tf_divergence_matrix(price_data_map, multi_cvd, lookback=5)
    print("📊 CVD Divergence Matrix:", divergence_matrix)

    # Contextual conditions (placeholder logic)
    vwap_relation = "failing reclaim"
    delta_behavior = "spike_no_follow"

    # Score sniper signal
    result = score_cvd_signal_from_matrix(divergence_matrix, vwap_relation, delta_behavior)

    # Fire alert if sniper-grade setup
    if result["score"] > 60:
        memory.log_event(data["timestamp"], cvd_value, data["price"], divergence_matrix, result["score"])

        msg = f"""
🎯 **LIVE SNIPER TRAP DETECTED**
**Score:** {result['score']}
**Setup:** {result['setup']}
**Price:** {data['price']}
**CVD Divergence Matrix:** {divergence_matrix}
**Reasons:**
- {'\n- '.join(result['reasons'])}
"""
        print(msg)
        send_discord_alert(msg)
    else:
        print(f"↪ No sniper trap | Score: {result['score']} | Matrix: {divergence_matrix}")

# Start feed loop
async def main():
    feed = BybitFeed()
    await feed.connect(on_tick)

if __name__ == "__main__":
    asyncio.run(main())
