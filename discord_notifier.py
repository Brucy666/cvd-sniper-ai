# discord_notifier.py

import os
import requests

WEBHOOKS = {
    "BTCUSDT": os.getenv("BTC_WEBHOOK")
}

def format_matrix(matrix):
    return "\n".join([f"- {tf}: {val}" for tf, val in matrix.items()])

def format_insights(insights):
    if not insights:
        return "None"
    return "\n".join([
        f"- [{i['tf']}] {i['trap_type']} (conf: {i['confidence']})"
        for i in insights
    ])

def send_discord_alert(symbol, result, price, matrix, vwap_status, insights=[]):
    symbol = symbol.upper()
    url = WEBHOOKS.get(symbol)

    if not url:
        print(f"⚠️ No webhook configured for {symbol}")
        return

    color = "🔴" if result["score"] >= 80 else "🟡"
    header = f"{color} **{symbol} SNIPER ALERT**"
    score_line = f"**Score:** `{result['score']}`  |  **Setup:** `{result['setup']}`"
    price_line = f"**Price:** `{price}`"
    vwap_line = f"📍 **VWAP Status:** `{vwap_status}`"
    matrix_block = f"📊 **CVD Divergence:**\n{format_matrix(matrix)}"
    insight_block = f"🧠 **Trap Insight(s):**\n{format_insights(insights)}"
    reasons = "\n- " + "\n- ".join(result["reasons"]) if result["reasons"] else "None"

    msg = f"""{header}
{score_line}
{price_line}
{vwap_line}
{matrix_block}
{insight_block}
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
            print(f"✅ Alert sent to #{symbol.lower()} channel")
    except Exception as e:
        print(f"❌ Discord send error: {e}")
