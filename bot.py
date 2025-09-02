import requests
import sqlite3
from random import randint
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# ---------------- CONFIG ----------------
BOT_TOKEN = "8277485140:AAERBu7ErxHReWZxcYklneU1wEXY--I_32c"
API_TOKEN = "7658050410:qQ88TxXl"
PEOPLE_API_URL = "https://leakosintapi.com/"
VEHICLE_API_URL = "https://vehicleinfo.zerovault.workers.dev/"
BOT_USERNAME = "Hahwjahjjahabot"
OWNER_USERNAME = "@CodeWraiithHere"

CHANNEL_1_LINK = "https://t.me/+pZ17mKu0yZYwYmVl"
CHANNEL_1_ID = "-1002851939876"
CHANNEL_2_LINK = "https://t.me/taskblixosint"
CHANNEL_2_ID = "-1002321550721"

UNLIMITED_USERS = [5145179256, 8270660057]

# ---------- DATABASE ----------
conn = sqlite3.connect('users.db', check_same_thread=False)

def execute_db(query, params=(), fetch=False):
    cur = conn.cursor()
    cur.execute(query, params)
    result = cur.fetchone() if fetch else None
    conn.commit()
    cur.close()
    return result

execute_db('''CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    credits INTEGER DEFAULT 3,
    ref_by TEXT
)''')

def add_user(user_id, ref_by=None):
    execute_db("INSERT OR IGNORE INTO users (user_id, credits, ref_by) VALUES (?, ?, ?)",
               (str(user_id), 3, ref_by))

def use_credit(user_id):
    if user_id in UNLIMITED_USERS:
        return True
    row = execute_db("SELECT credits FROM users WHERE user_id=?", (str(user_id),), fetch=True)
    if row and row[0] > 0:
        execute_db("UPDATE users SET credits=credits-1 WHERE user_id=?", (str(user_id),))
        return True
    return False

def get_credits(user_id):
    if user_id in UNLIMITED_USERS:
        return "Unlimited"
    row = execute_db("SELECT credits FROM users WHERE user_id=?", (str(user_id),), fetch=True)
    return row[0] if row else 0

def add_referral(ref_user_id):
    # Give credit only if the referred user exists
    ref_row = execute_db("SELECT user_id FROM users WHERE user_id=?", (str(ref_user_id),), fetch=True)
    if ref_row:
        execute_db("UPDATE users SET credits=credits+1 WHERE user_id=?", (str(ref_user_id),))

def get_referral_link(user_id):
    return f"https://t.me/{BOT_USERNAME}?start=REF{user_id}"

def generate_people_report(phone):
    data = {"token": API_TOKEN, "request": phone, "limit": 300, "lang": "en"}
    try:
        response = requests.post(PEOPLE_API_URL, json=data).json()
    except:
        return "❌ API returned invalid response"
    if "Error code" in response:
        return "❌ No results found"
    result_texts = []
    for db_name in response.get("List", {}):
        db_result = response["List"][db_name]
        for record in db_result.get("Data", []):
            lines = []
            if "FullName" in record: lines.append(f"🧑 Name: {record['FullName']}")
            if "FatherName" in record: lines.append(f"👨 Father's Name: {record['FatherName']}")
            if "DocNumber" in record: lines.append(f"🆔 Document Number: {record['DocNumber']}")
            if "Region" in record: lines.append(f"📍 Region: {record['Region']}")
            if "Address" in record: lines.append(f"🏠 Address: {record['Address']}")
            phone_list = [v for k,v in record.items() if k.startswith("Phone")]
            if phone_list:
                phone_lines = "\n".join([f"  {i+1}️⃣ {p}" for i,p in enumerate(phone_list)])
                lines.append(f"📞 Phones:\n{phone_lines}")
            result_texts.append("\n".join(lines))
    if not result_texts:
        return "❌ No results found"
    return "\n\n".join(result_texts)

def generate_vehicle_report(vin):
    try:
        response = requests.get(VEHICLE_API_URL, params={"VIN": vin}).json()
        if "error" in response:
            return f"❌ Vehicle info not found for VIN: {vin}"
        lines = ["🚗 VEHICLE INFORMATION"]
        for k, v in response.items():
            if isinstance(v, bool):
                v = "✅" if v else "❌"
            lines.append(f"{k.replace('_',' ').title()}: {v}")
        return "\n".join(lines)
    except:
        return f"❌ Failed to fetch vehicle info for VIN: {vin}"

bot = telebot.TeleBot(BOT_TOKEN)

def check_joined(user_id):
    return True

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    ref_by = None
    is_new_user = False

    # Check if user exists
    row = execute_db("SELECT user_id FROM users WHERE user_id=?", (str(user_id),), fetch=True)
    if not row:
        is_new_user = True

    # Handle referral only for new users
    if message.text.startswith("/start REF") and is_new_user:
        ref_code = message.text.split("REF")[1]
        ref_by = ref_code
        add_referral(ref_by)
        bot.send_message(user_id, f"🎉 1 credit added for referral!")

    # Add user if new
    if is_new_user:
        add_user(user_id, ref_by)

    if not check_joined(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Join Channel 1", url=CHANNEL_1_LINK))
        markup.add(InlineKeyboardButton("Join Channel 2", url=CHANNEL_2_LINK))
        bot.send_message(user_id, "⚠️ Please join our channels first to use the bot", reply_markup=markup)
        return

    show_main_menu(user_id)

def show_main_menu(user_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("📞 Number Info", callback_data="number"),
        InlineKeyboardButton("🚗 Vehicle Info", callback_data="vehicle"),
        InlineKeyboardButton("💳 Check Balance", callback_data="balance"),
        InlineKeyboardButton("🔗 Referral", callback_data="referral"),
        InlineKeyboardButton("🤖 Clone My Bot", callback_data="clone"),
        InlineKeyboardButton("👤 Contact Owner", callback_data="owner")
    )
    bot.send_message(user_id, "👋 Welcome!\nSelect an option:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call: CallbackQuery):
    user_id = call.from_user.id
    if call.data == "number":
        msg = bot.send_message(user_id, "📞 Enter phone number with country code (e.g., 919XXXXXXXXX):")
        bot.register_next_step_handler(msg, process_number)
    elif call.data == "vehicle":
        msg = bot.send_message(user_id, "🚗 Enter vehicle VIN or number:")
        bot.register_next_step_handler(msg, process_vehicle)
    elif call.data == "balance":
        credits = get_credits(user_id)
        bot.send_message(user_id, f"💳 Your credits: {credits}")
    elif call.data == "referral":
        bot.send_message(user_id, f"🔗 Your referral link:\n{get_referral_link(user_id)}")
    elif call.data == "clone":
        bot.send_message(user_id, "🔗 Enter your bot token to clone your bot (Backend remains on main server)")
    elif call.data == "owner":
        bot.send_message(user_id, f"👤 Contact Owner: {OWNER_USERNAME}")

def process_number(message):
    user_id = message.from_user.id
    phone = message.text.strip()
    bot.send_message(user_id, f"📞 Processing number info for {phone}...\n⏳ Please wait...")
    if use_credit(user_id):
        result = generate_people_report(phone)
        bot.send_message(user_id, result)
    else:
        bot.send_message(user_id, "❌ You don't have enough credits.")
    show_main_menu(user_id)

def process_vehicle(message):
    user_id = message.from_user.id
    vin = message.text.strip()
    bot.send_message(user_id, f"🚗 Processing vehicle info for {vin}...\n⏳ Please wait...")
    if use_credit(user_id):
        result = generate_vehicle_report(vin)
        bot.send_message(user_id, result)
    else:
        bot.send_message(user_id, "❌ You don't have enough credits.")
    show_main_menu(user_id)

print("🤖 Bot is running...")
bot.infinity_polling()
