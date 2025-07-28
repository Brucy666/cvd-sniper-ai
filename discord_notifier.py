# discord_notifier.py

import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1399312421130076300/sOdMLGErToxhZOVt_SqTVzvfAVYk5mV9ILCpCr-vMyf97ME4t9ZAxWq5quudkbbiKyGx"

def send_discord_alert(symbol, result, price, matrix):
    """
    Sends a formatted sniper trap alert to Discord.

    Args:
        symbol (str): Asset symbol like BTCUSDT
        result (dict): From score_cvd_signal_from_matrix
        price (float): Latest price
        matrix (dict): Divergence matrix
    """
    color = "🔴" if result["score"] >= 70 else "🟡"
    header = f"{color} **{symbol} SNIPER ALERT**"
    score_line = f"**Score:** `{result['score']}`  |  **Setup:** `{result['setup']}`"
    price_line = f"**Price:** `{price}`"
    matrix_line = f"**CVD Divergence Matrix:** `{matrix}`"

    reasons = "\n- " + "\n- ".join(result["reasons"]) if result["reasons"] else "None"

    msg = f"""{header}
{score_line}
{price_line}
{matrix_line}
**Reasons:**{reasons}
"""
    payload = {"content": msg.strip()}

    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print(f"✅ Alert sent for {symbol}")
        else:
            print(f"⚠️ Discord error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Discord webhook failed: {e}")
