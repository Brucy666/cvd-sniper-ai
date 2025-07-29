# supabase_writer.py

import requests
import datetime
import os

SUPABASE_URL = "https://jlnlwohutrnijiuxchna.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "YOUR_SERVICE_ROLE_KEY_HERE"
SUPABASE_TABLE = "Traps"

headers = {
    "apikey": SUPABASE_KEY,  # ✅ must use apikey, not Authorization
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
        print("\n📡 Inserting trap into Supabase...")
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}",
            headers=headers,
            json=payload
        )

        if response.status_code in [200, 201]:
            print(f"✅ Supabase insert success | {symbol} | Score: {score}")
        else:
            print(f"❌ Supabase insert failed | Code: {response.status_code} | Msg: {response.text}")

    except Exception as e:
        print(f"❌ Exception inserting to Supabase: {e}")
