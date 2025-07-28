# discord_notifier.py

import os
import requests

WEBHOOKS = {
    "BTCUSDT": os.getenv("BTC_WEBHOOK")
}

TREND_EMOJIS = {
    "uptrend": "🔺",
    "downtrend": "🔻",
    "range": "🔄",
    "transition": "⚠️",
    "compressing": "📉",
    "unknown": "❓"
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

def format_bias_stack(bias_stack):
    if not bias_stack:
        return ""

    def format_line(level):
        bias = bias_stack[level]["bias"]
        trend = bias_stack[level].get("trend", "unknown")
        emoji = TREND_EMOJIS.get(trend, "❓")
        return f"- {level.capitalize()}: `{bias}` (trend: {trend}) {emoji}"

    lines = "\n".join([
        format_line("low"),
        format_line("mid"),
        format_line("high")
    ])
    
    return f"""
🧠 **Bias Stack:**
{lines}
📊 Alignment: `{bias_stack['alignment']}`
"""

def send_discord_alert(symbol, result, price, matrix, vwap_status, insights=[], bias_stack=None):
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
    insight_block = f"🧠 **Trap Insights:**\n{format_insights(insights)}"
    bias_block = format_bias_stack(bias_stack)
    reasons = "\n- " + "\n- ".join(result["reasons"]) if result["reasons"] else "None"

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
            print(f"⚠️ Response content: {response.text}")
        else:
            print(f"✅ Alert delivered to #{symbol.lower()} channel")
    except Exception as e:
        print(f"❌ Discord send error for {symbol}: {e}")
