# trap_outcome_updater.py

import requests
import datetime
import time

SUPABASE_URL = "https://jlnlwohutrnijiuxchna.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impsbmx3b2h1dHJuaWppdXhjaG5hIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mzc2NzIyNiwiZXhwIjoyMDY5MzQzMjI2fQ.8BKE7OucjwTMjfLA0qNyu0mIlW5yIAn7OP2Ibi64FcY"
SUPABASE_TABLE = "Traps"
OUTCOME_WINDOW_SECONDS = 600  # 10-minute evaluation window

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def fetch_traps_needing_outcome():
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?outcome_success=is.null&select=*"
    r = requests.get(url, headers=headers)
    return r.json() if r.status_code == 200 else []

def mock_live_price(symbol):
    # TODO: Replace with live price API call
    return 117800.0 if symbol == "BTCUSDT" else 0.0

def evaluate_trap(trap):
    trap_time = datetime.datetime.fromisoformat(trap["timestamp"].replace("Z", ""))
    now = datetime.datetime.utcnow()
    elapsed = (now - trap_time).total_seconds()

    if elapsed < OUTCOME_WINDOW_SECONDS:
        return None

    price_now = mock_live_price(trap["symbol"])
    entry_price = trap["price"]
    delta = round(price_now - entry_price, 2)

    if "buyer" in trap["trap_type"]:
        outcome = price_now > entry_price
    elif "seller" in trap["trap_type"]:
        outcome = price_now < entry_price
    else:
        outcome = abs(delta) > 25  # default trap outcome logic

    return {
        "outcome_success": outcome,
        "delta": delta
    }

def update_trap(trap, result):
    if not result:
        return

    update_url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?timestamp=eq.{trap['timestamp']}&bot_id=eq.{trap['bot_id']}"
    r = requests.patch(update_url, headers=headers, json=result)
    print(f"✅ Updated trap at {trap['timestamp']} | Outcome: {result['outcome_success']} | Δ: {result['delta']}")

def run():
    print("🔍 Checking for traps needing outcome updates...")
    traps = fetch_traps_needing_outcome()
    for trap in traps:
        result = evaluate_trap(trap)
        if result:
            update_trap(trap, result)

if __name__ == "__main__":
    while True:
        run()
        time.sleep(60)  # check every 60 seconds
