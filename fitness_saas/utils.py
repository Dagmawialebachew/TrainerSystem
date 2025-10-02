import requests
from django.conf import settings

def notify_bot(message: str):
    """
    Send a message to Telegram bot.
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    try:
        requests.post(url, data=payload, timeout=5)
    except requests.exceptions.RequestException as e:
        # Log error but don’t break user flow
        print(f"Bot notification failed: {e}")
