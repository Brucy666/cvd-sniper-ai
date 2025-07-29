# supabase_writer.py

import requests
import datetime
import os

SUPABASE_URL = "https://jlnlwohutrnijiuxchna.supabase.co"
SUPABASE_TABLE = "Traps"

# Grab from Railway environment or fallback
SUPABASE_KEY = (os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "sb_secret_eFtCTuYaVmjhOC1lrkTRvg_yNiu7bR-").strip()

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}


def log_trap_to_supabase(
    bot_id: str,
    symbol: str,
    price: float,
    score: int,
    trap_type: str,
    confidence: int,
    bias_alignment: str,
    outcome_success: bool = None,
    delta: float = None
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

    print("\n📡 Attempting Supabase trap insert...")
    print(f"🔑 Key loaded: {'VALID' if SUPABASE_KEY.startswith('sb_') else 'INVALID'}")
    print(f"🛣 Endpoint: {SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}")
    print("📦 Payload:", payload)

    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}",
            headers=headers,
            json=payload
        )
        if response.status_code in [200, 201]:
            print(f"✅ Supabase insert successful | {symbol} | {score} pts")
        else:
            print(f"❌ Supabase error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Exception during Supabase insert: {e}")
