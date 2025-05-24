# Send push notifications with telegram
# Author: derMax450

import requests
from configLoader import load_config

# Load telegram config
telegram_config = load_config("telegram")

TOKEN = telegram_config["token"]
CHAT_ID = telegram_config["chat_id"]

def send_telegram_message(text, parse_mode=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode

    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram message sent.")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP error: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")

