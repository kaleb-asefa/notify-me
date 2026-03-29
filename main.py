# bot_sms.py
import os
import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
from config import api_token, TEXTBEE_API_KEY, TEXTBEE_DEVICE_ID, phone_number
from logic import process_message

# === TextBee API setup ===

TEXTBEE_URL = f"https://api.textbee.dev/api/v1/gateway/devices/{TEXTBEE_DEVICE_ID}/send-sms"

# The phone number to receive SMS
SMS_RECIPIENT = phone_number  # replace with the real phone number

# === Telegram bot setup ===
bot = telebot.TeleBot(token=api_token)

# @bot.message_handler(regexp='(?i)update')
# def forward_to_sms(message):
#     if message.chat.type not in ["group", "supergroup"]:
#         return

#     text = message.text or "[non-text message]"
#     sms_text = f"From group ({message.chat.title}):\n{text}"

#     # Send SMS via TextBee
#     payload = {"recipients": [SMS_RECIPIENT], "message": sms_text}
#     headers = {"x-api-key": TEXTBEE_API_KEY, "Content-Type": "application/json"}
#     try:
#         requests.post(TEXTBEE_URL, json=payload, headers=headers)
#     except Exception as e:
#         print("SMS send failed:", e)

#     # Optional: reply in group to acknowledge
#     try:
#         bot.reply_to(message, "This message was sent as SMS.")
#     except:
#         pass



# ---------------- RUN BOT ----------------
print("Bot is running...")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if process_message(message.text):
        bot.reply_to(message, "Message processed for update detection.")
    else:
        print(f"Not an update: {message.text}")

bot.polling()
