# discord_notifier.py

import os
import requests

# Use Railway environment variables
WEBHOOKS = {
    "BTCUSDT": os.getenv("BTC_WEBHOOK"),
    # You can add more:
    # "ETHUSDT": os.getenv("ETH_WEBHOOK"),
    # "SOLUSDT": os.getenv("SOL_WEBHOOK")
}

def format_matrix(matrix):
    return "\n".join([f"- {tf}: {val}" for tf, val in matrix.items()])

def send_discord_alert(symbol, result, price, matrix):
    symbol = symbol.upper()
    url = WEBHOOKS.get(symbol)

    if not url:
        print(f"⚠️ No webhook configured for {symbol}")
        return

    color = "🔴" if result["score"] >= 80 else "🟡"
    header = f"{color} **{symbol} SNIPER ALERT**"
    score_line = f"**Score:** `{result['score']}`  |  **Setup:** `{result['setup']}`"
    price_line = f"**Price:** `{price}`"

    matrix_block = f"🕒 **CVD Divergence:**\n{format_matrix(matrix)}"
    reasons = "\n- " + "\n- ".join(result["reasons"]) if result["reasons"] else "None"

    msg = f"""{header}
{score_line}
{price_line}
{matrix_block}
**Reasons:**{reasons}
"""

    payload = {"content": msg.strip()}

    try:
        print(f"📤 Sending alert for {symbol}...")
        response = requests.post(url, json=payload)
        print(f"📡 Discord response {symbol}: {response.status_code}")
        if response.status_code != 204:
            print(f"⚠️ Response content: {response.text}")
        else:
            print(f"✅ Alert delivered to #{symbol.lower()} channel")
    except Exception as e:
        print(f"❌ Error sending alert for {symbol}: {e}")
