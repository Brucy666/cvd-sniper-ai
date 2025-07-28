import requests
import os

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_SNIPER")  # Set in your .env

def format_matrix(matrix):
    return ", ".join([f"{tf}: {val}" for tf, val in matrix.items()])

def send_discord_alert(result: str, price: float, matrix: dict):
    formatted_matrix = format_matrix(matrix)
    message = {
        "content": (
            f"📡 **Sniper Status Update**\n"
            f"> **Result**: {result}\n"
            f"> **Price**: `{price}`\n"
            f"> **CVD Matrix**: `{formatted_matrix}`"
        )
    }
    try:
        requests.post(DISCORD_WEBHOOK, json=message)
    except Exception as e:
        print(f"❌ Discord alert failed: {e}")
