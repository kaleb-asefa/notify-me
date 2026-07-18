import logging
import sys
from typing import NoReturn

import requests
import telebot
from telebot.types import Message

from config import (
    SMS_RECIPIENT,
    TELEGRAM_BOT_TOKEN,
    TEXTBEE_API_KEY,
    TEXTBEE_DEVICE_ID,
)
from logic import process_message

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("bot")

# ---------------------------------------------------------------------------
# TextBee SMS gateway
# ---------------------------------------------------------------------------

TEXTBEE_URL = (
    f"https://api.textbee.dev/api/v1/gateway/devices/"
    f"{TEXTBEE_DEVICE_ID}/send-sms"
)


def send_sms(text: str) -> None:
    """Send an SMS notification via the TextBee API."""
    payload = {"recipients": [SMS_RECIPIENT], "message": text}
    headers = {"x-api-key": TEXTBEE_API_KEY, "Content-Type": "application/json"}
    try:
        resp = requests.post(TEXTBEE_URL, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        logger.info("SMS sent successfully")
    except requests.RequestException as exc:
        logger.warning("Failed to send SMS: %s", exc)


# ---------------------------------------------------------------------------
# Telegram bot
# ---------------------------------------------------------------------------

bot = telebot.TeleBot(token=TELEGRAM_BOT_TOKEN)


@bot.message_handler(func=lambda message: True)
def handle_message(message: Message) -> None:
    """Route every incoming group message through the update detector."""
    try:
        if process_message(message.text):
            bot.reply_to(message, "Update detected and logged.")
            logger.info("Update: %s", message.text)
    except Exception:
        logger.exception("Error processing message")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> NoReturn:
    """Start the Telegram bot polling loop."""
    logger.info("Bot is running ...")
    bot.polling(none_stop=True)


if __name__ == "__main__":
    main()
