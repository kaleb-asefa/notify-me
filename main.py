# bot_sms.py
import os
import telebot
import requests
from config import api_token, TEXTBEE_API_KEY, TEXTBEE_DEVICE_ID

# === TextBee API setup ===

TEXTBEE_URL = f"https://api.textbee.dev/api/v1/gateway/devices/{TEXTBEE_DEVICE_ID}/send-sms"

# The phone number to receive SMS
SMS_RECIPIENT = "+251991135255"  # replace with the real phone number

# === Telegram bot setup ===
bot = telebot.TeleBot(token=api_token)

@bot.message_handler(regexp='(?i)update')
def forward_to_sms(message):
    if message.chat.type not in ["group", "supergroup"]:
        return

    text = message.text or "[non-text message]"
    sms_text = f"From group ({message.chat.title}):\n{text}"

    # Send SMS via TextBee
    payload = {"recipients": [SMS_RECIPIENT], "message": sms_text}
    headers = {"x-api-key": TEXTBEE_API_KEY, "Content-Type": "application/json"}
    try:
        requests.post(TEXTBEE_URL, json=payload, headers=headers)
    except Exception as e:
        print("SMS send failed:", e)

    # Optional: reply in group to acknowledge
    try:
        bot.reply_to(message, "This message was sent as SMS.")
    except:
        pass

# Start polling
bot.infinity_polling()