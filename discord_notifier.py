# discord_notifier.py

import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1399312421130076300/sOdMLGErToxhZOVt_SqTVzvfAVYk5mV9ILCpCr-vMyf97ME4t9ZAxWq5quudkbbiKyGx"

def send_discord_alert(message: str):
    """
    Sends a message to a Discord webhook.
    Args:
        message (str): The content to send.
    """
    if not WEBHOOK_URL:
        print("❌ Webhook URL is missing.")
        return

    payload = {"content": message.strip()}

    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print("✅ Alert sent to Discord.")
        else:
            print(f"⚠️ Discord error: {response.status_code} | {response.text}")
    except Exception as e:
        print(f"❌ Discord webhook exception: {e}")
