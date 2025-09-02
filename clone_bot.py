from telebot import TeleBot, types

# Aapke main bot ka token
MAIN_BOT_TOKEN = "8277485140:AAERBu7ErxHReWZxcYklneU1wEXY--I_32c"
OWNER_USERNAME = "@CodeWraiithHere"

bot = TeleBot(MAIN_BOT_TOKEN, parse_mode="Markdown")

# Start command
@bot.message_handler(commands=["start"])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🤖 Clone My Bot", callback_data="clone")
    markup.add(btn)
    bot.send_message(message.chat.id,
        "👋 Welcome!\n\n"
        "Yaha se aap apna **clone bot** bana sakte ho.",
        reply_markup=markup
    )

# Clone option
@bot.callback_query_handler(func=lambda call: call.data == "clone")
def clone_request(call):
    msg = bot.send_message(call.message.chat.id,
        "🤖 Send me your **Bot Token**\n\n"
        "👉 Token kaise nikale:\n"
        "1. Telegram pe search karo: @BotFather\n"
        "2. Command bhejo: /newbot\n"
        "3. Bot ka naam aur username set karo\n"
        "4. BotFather aapko ek token dega (eg: `123456:ABC-DEF1234...`).\n\n"
        "⚠️ Apna token yahi bhejo!"
    )
    bot.register_next_step_handler(msg, process_clone_token)

# Token process
def process_clone_token(message):
    token = message.text.strip()
    if ":" not in token:
        bot.send_message(message.chat.id, "❌ Invalid token. Please try again.")
        return
    
    bot.send_message(message.chat.id,
        f"✅ Token received!\n\n"
        f"Ab apna clone bot run karne ke liye yeh steps follow karo:\n\n"
        f"1. Termux ya Server open karo\n"
        f"2. Repo clone karo: `git clone https://github.com/dipakmori0/PHONE.git`\n"
        f"3. `bot.py` open karke apna token paste karo: `{token}`\n"
        f"4. Run command: `python3 bot.py`\n\n"
        f"👤 Help ke liye contact: {OWNER_USERNAME}"
    )

print("🤖 Clone Bot System is running...")
bot.infinity_polling()
