# main.py

from cvd_engine import CVDEngine
from cvd_divergence_detector import detect_cvd_divergence
from cvd_ai_score import score_cvd_signal
from cvd_memory_store import CVDMemoryStore
from discord_notifier import send_discord_alert
import time

# Initialize core modules
cvd = CVDEngine()
memory = CVDMemoryStore()

# Simulated test feed (replace later with live price + volume)
price_feed = [100, 101, 102, 103, 104, 105, 106, 107, 108, 107]
buy_volumes = [200, 220, 210, 230, 240, 180, 170, 160, 150, 140]
sell_volumes = [190, 200, 205, 210, 220, 200, 180, 180, 180, 180]

# Loop over fake feed to simulate sniper detection
for i in range(len(price_feed)):
    timestamp = time.time()
    
    # Update CVD with new delta
    cvd_value = cvd.update(
        buy_volume=buy_volumes[i],
        sell_volume=sell_volumes[i],
        timestamp=timestamp
    )

    # Extract last few price + CVD points
    price_slice = price_feed[max(0, i - 5): i + 1]
    cvd_slice = [entry['cvd'] for entry in cvd.get_recent_deltas(len(price_slice))]

    # Detect divergence
    divergence = detect_cvd_divergence(price_slice, cvd_slice)

    # Mock confluence conditions (replace later)
    vwap_relation = "failing reclaim"
    delta_behavior = "spike_no_follow"

    # Score the sniper setup
    result = score_cvd_signal(divergence, vwap_relation, delta_behavior)

    # If valid sniper signal, log + alert
    if result["score"] > 60:
        memory.log_event(timestamp, cvd_value, price_feed[i], divergence, result["score"])

        alert_msg = f"""
🎯 **SNIPER SIGNAL @ i={i}**
**Score:** {result['score']}
**Setup:** {result['setup']}
**Reasons:**
- {'\n- '.join(result['reasons'])}
"""
        print(alert_msg)
        send_discord_alert(alert_msg)

    else:
        print(f"↪ No valid signal @ i={i} | Score: {result['score']}")
