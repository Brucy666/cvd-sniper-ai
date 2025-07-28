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

def send_discord_alert(symbol, result, price, matrix, vwap_status, insights=[], htf_bias=None):
    symbol = symbol.upper()
    url = WEBHOOKS.get(symbol)

    if not url:
        print(f"⚠️ No webhook for {symbol}")
        return

    color = "🔴" if result["score"] >= 80 else "🟡"
    header = f"{color} **{symbol} SNIPER ALERT**"
    score_line = f"**Score:** `{result['score']}`  |  **Setup:** `{result['setup']}`"
    price_line = f"**Price:** `{price}`"
    vwap_line = f"📍 **VWAP Status:** `{vwap_status}`"

    matrix_block = f"📊 **CVD Divergence:**\n{format_matrix(matrix)}"
    insight_block = f"🧠 **Trap Insights:**\n{format_insights(insights)}"
    reasons = "\n- " + "\n- ".join(result["reasons"]) if result["reasons"] else "None"

    bias_block = ""
    if htf_bias:
        bias_block = f"\n🧠 **HTF Bias:** `{htf_bias['htf_bias']}` | Structure: `{htf_bias['structure']}` | Trap focus: `{htf_bias['preferred_trap']}`"

    msg = f"""{header}
{score_line}
{price_line}
{vwap_line}
{matrix_block}
{insight_block}
{bias_block}
**Reasons:**{reasons}
"""

    try:
        print(f"📤 Sending alert for {symbol}...")
        response = requests.post(url, json={"content": msg.strip()})
        print(f"📡 Discord response {symbol}: {response.status_code}")
        if response.status_code != 204:
            print(f"⚠️ Discord error: {response.text}")
    except Exception as e:
        print(f"❌ Discord send error: {e}")
