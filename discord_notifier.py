# discord_notifier.py

import requests
import os

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")  # set this in Railway .env

def send_discord_alert(message: str):
    if not DISCORD_WEBHOOK_URL:
        print("❌ DISCORD_WEBHOOK_URL not set.")
        return

    payload = {
        "content": message
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code != 204:
            print(f"⚠️ Discord response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Discord error: {e}")
