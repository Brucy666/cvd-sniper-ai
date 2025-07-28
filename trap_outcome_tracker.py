# trap_outcome_tracker.py

import json
import os
from datetime import datetime, timedelta

LOG_FILE = "trap_log.json"
OUTCOME_WINDOW_SECONDS = 600  # 10 minutes


def update_outcomes(current_price, current_time):
    if not os.path.exists(LOG_FILE):
        print("❌ Trap log file not found.")
        return

    with open(LOG_FILE, "r") as f:
        try:
            traps = json.load(f)
        except json.JSONDecodeError:
            print("❌ Failed to parse trap log.")
            return

    updated = False

    for trap in traps:
        if trap.get("outcome") is not None:
            continue  # already evaluated

        trap_time = datetime.fromisoformat(trap["timestamp"])
        elapsed = (datetime.utcfromtimestamp(current_time) - trap_time).total_seconds()

        if elapsed < OUTCOME_WINDOW_SECONDS:
            continue  # too soon

        trap_price = trap["price"]
        delta = current_price - trap_price
        direction = trap["trap_insights"][0]["trap_type"].lower()

        # Basic outcome classification
        if "buyer trap" in direction or "short" in trap["alert"]["reasons"][0].lower():
            success = delta < -25  # price dropped
        elif "seller trap" in direction or "long" in trap["alert"]["reasons"][0].lower():
            success = delta > 25  # price went up
        else:
            success = abs(delta) >= 25

        trap["outcome"] = {
            "success": success,
            "delta": round(delta, 2),
            "evaluated_at": datetime.utcfromtimestamp(current_time).isoformat()
        }
        updated = True
        print(f"📈 Trap outcome updated | Δ: {delta:.2f} | Success: {success}")

    if updated:
        with open(LOG_FILE, "w") as f:
            json.dump(traps, f, indent=2)
        print("✅ Trap journal updated with outcomes.")
    else:
        print("🕒 No trap outcomes updated yet.")
