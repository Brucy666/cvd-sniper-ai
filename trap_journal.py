# trap_journal.py

import json
import os
from datetime import datetime

LOG_FILE = "trap_log.json"


def log_full_trap(
    symbol,
    price,
    timestamp,
    divergence_matrix,
    trap_insights,
    vwap_status,
    fib_result=None,
    bias_stack=None,
    alert_score=None,
    alert_reasons=None,
    outcome=None  # Placeholder for future result tracking
):
    entry = {
        "timestamp": datetime.utcfromtimestamp(timestamp).isoformat(),
        "symbol": symbol,
        "price": round(price, 2),
        "divergence_matrix": divergence_matrix,
        "trap_insights": trap_insights,
        "vwap_status": vwap_status,
        "bias_stack": bias_stack,
        "fib_trap": {
            "triggered": fib_result.get("triggered") if fib_result else False,
            "zone": list(map(lambda x: round(x, 2), fib_result.get("zone", []))) if fib_result else [],
            "confidence": fib_result.get("confidence") if fib_result else None,
            "reason": fib_result.get("reason") if fib_result else None
        },
        "alert": {
            "score": alert_score,
            "reasons": alert_reasons,
            "triggered": alert_score is not None and alert_score > 60
        },
        "outcome": outcome  # To be filled later
    }

    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

    logs.append(entry)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

    print(f"📚 Trap logged @ {price} | Score: {alert_score} | Fib: {fib_result.get('triggered') if fib_result else False}")
