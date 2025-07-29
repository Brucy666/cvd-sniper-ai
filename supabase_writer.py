# supabase_writer.py

import requests
import datetime
import os

SUPABASE_URL = "https://jlnlwohutrnijiuxchna.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Add this to Railway env vars
SUPABASE_TABLE = "traps"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}


def log_trap_to_supabase(
    bot_id,
    symbol,
    price,
    score,
    trap_type,
    confidence,
    bias_alignment,
    outcome_success=None,
    delta=None
):
    payload = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "bot_id": bot_id,
        "symbol": symbol,
        "price": round(price, 2),
        "score": score,
        "trap_type": trap_type,
        "confidence": confidence,
        "bias_alignment": bias_alignment,
        "outcome_success": outcome_success,
        "delta": round(delta, 2) if delta is not None else None
    }

    try:
        res = requests.post(
            f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}",
            headers=headers,
            json=payload
        )
        if res.status_code in [200, 201]:
            print(f"☁️ Trap uploaded to Supabase | {symbol} | {score} pts")
        else:
            print(f"❌ Supabase error {res.status_code}: {res.text}")
    except Exception as e:
        print(f"❌ Failed to upload trap: {e}")
