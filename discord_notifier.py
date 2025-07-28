# discord_notifier.py

import requests

# Channel-specific webhooks
WEBHOOKS = {
    "BTCUSDT": "https://discord.com/api/webhooks/1399375599847477278/GvpDMz7vsNEVHaipwjrISy_w21X5EOCrQVikQo7E59UkJkWZPy3yhAptruf95U1xRl2O",
    "ETHUSDT": "https://discord.com/api/webhooks/1399376610259501167/KB5Mk2W9NQM5YrqhYKRogL8bSk8DufnHz3zaHdw-B1cL-xNTGXBE9DML4arfGAYVIk5-",
    "SOLUSDT": "https://discord.com/api/webhooks/1399376272622223521/-WBsGnn-4VeIv-OWC6bb1sYHEDLzY0fwJJ7Wfbqyk-PDISSV0zZddN2ijybst716TyOU"
}

def send_discord_alert(symbol, result, price, matrix):
    url = WEBHOOKS.get(symbol)
    if not url:
        print(f"⚠️ No webhook found for symbol {symbol}")
        return

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
        response = requests.post(url, json=payload)
        if response.status_code == 204:
            print(f"✅ Alert sent to #{symbol.lower()} channel")
        else:
            print(f"⚠️ Discord error [{symbol}]: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Webhook failure [{symbol}]: {e}")
