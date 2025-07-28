# main.py

from cvd_engine import CVDEngine
from cvd_divergence_detector import detect_cvd_divergence
from cvd_ai_score import score_cvd_signal
from cvd_memory_store import CVDMemoryStore
import time

cvd = CVDEngine()
memory = CVDMemoryStore()

# Simulated data (replace with real feed later)
price_feed = [100, 101, 102, 103, 104, 105, 106, 107, 108, 107]
buy_vols = [200, 220, 210, 230, 240, 180, 170, 160, 150, 140]
sell_vols = [190, 200, 205, 210, 220, 200, 180, 180, 180, 180]

for i in range(len(price_feed)):
    cvd_value = cvd.update(buy_vols[i], sell_vols[i], timestamp=time.time())
    
    price_slice = price_feed[max(0, i-5):i+1]
    cvd_slice = [entry['cvd'] for entry in cvd.get_recent_deltas(len(price_slice))]

    divergence = detect_cvd_divergence(price_slice, cvd_slice)
    result = score_cvd_signal(divergence, "failing reclaim", "spike_no_follow")

    if result["score"] > 60:
        memory.log_event(time.time(), cvd_value, price_feed[i], divergence, result["score"])
        print(f"🚨 SNIPER SIGNAL at i={i}: {result}")
    else:
        print(f"↪ No signal at i={i}")
