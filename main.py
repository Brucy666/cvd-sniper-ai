# main.py

from bybit_feed import BybitFeed
from cvd_engine import CVDEngine
from cvd_multi_tf_engine import MultiTimeframeCVDEngine
from multi_tf_divergence_matrix import detect_multi_tf_divergence_matrix
from cvd_ai_score import score_cvd_signal_from_matrix
from cvd_memory_store import CVDMemoryStore
from discord_notifier import send_discord_alert
import asyncio

# Settings
SYMBOL = "BTCUSDT"
MAX_HISTORY = 30

# Initialize engines
cvd = CVDEngine()
multi_cvd = MultiTimeframeCVDEngine()
memory = CVDMemoryStore()
price_history = []

# Track alert status to prevent spamming
alert_fired = False

async def on_tick(data):
    global alert_fired

    # Update CVD with new trade data
    cvd_value = cvd.update(data["buy_volume"], data["sell_volume"], data["timestamp"])
    multi_cvd.update(data["buy_volume"], data["sell_volume"], data["timestamp"])

    # Maintain price history
    price_history.append(data["price"])
    if len(price_history) > MAX_HISTORY:
        price_history.pop(0)

    # Prepare divergence check
    price_data_map = {
        "1m": price_history,
        "3m": price_history,
        "5m": price_history,
        "15m": price_history
    }

    divergence_matrix = detect_multi_tf_divergence_matrix(price_data_map, multi_cvd, lookback=5)
    print("📊 CVD Divergence Matrix:", divergence_matrix)

    # Placeholder logic
    vwap_relation = "failing reclaim"
    delta_behavior = "spike_no_follow"
    result = score_cvd_signal_from_matrix(divergence_matrix, vwap_relation, delta_behavior)

    # 🔧 DEBUG: Force test alert (optional)
    if not alert_fired:
        print(f"🧪 TEST: Forcing sniper alert for {SYMBOL}")
        result = {
            "score": 95,
            "setup": "sniper trap (TEST)",
            "reasons": ["FORCED TEST divergence", "simulated VWAP rejection", "delta spike"]
        }
        divergence_matrix = {
            "1m": "bearish",
            "3m": "bearish",
            "5m": "none",
            "15m": "none"
        }
        send_discord_alert(SYMBOL, result, data["price"], divergence_matrix)
        alert_fired = True
        return

    # Normal alert logic
    if result["score"] > 60:
        memory.log_event(data["timestamp"], cvd_value, data["price"], divergence_matrix, result["score"])
        send_discord_alert(SYMBOL, result, data["price"], divergence_matrix)
        alert_fired = True
    else:
        print(f"↪ No trap | Score: {result['score']}")

# Start feed
async def main():
    feed = BybitFeed(symbol=SYMBOL)
    await feed.connect(on_tick)

if __name__ == "__main__":
    asyncio.run(main())
