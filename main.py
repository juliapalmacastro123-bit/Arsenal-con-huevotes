import os
import telebot
from telebot import types
from flask import Flask, request
import subprocess
import traceback

# ======================
# CONFIG
# ======================

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
app = Flask(__name__)

BASE_URL = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_URL = f"{BASE_URL}/{TOKEN}" if BASE_URL else None

PAGO_LINK = "https://mpago.la/2KNKzJp"

ADMIN_ID = "7949397943"

# ======================
# STATE
# ======================

regions = {}

# ======================
# ADMIN
# ======================

def is_admin(user_id):
    return str(user_id) == ADMIN_ID

# ======================
# SAFE SEND
# ======================

def send(chat_id, text, kb=None):
    try:
        bot.send_message(chat_id, text, reply_markup=kb)
    except Exception as e:
        print("SEND ERROR:", e)

# ======================
# START
# ======================

@bot.message_handler(commands=["start"])
def start(m):

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🇲🇽 MX", "🌎 INTERNATIONAL")

    send(
        m.chat.id,
        "🎧 <b>ARSENAL AUDIO SYSTEM</b>\n\nChoose your region:",
        kb
    )

# ======================
# REGION LOCK
# ======================

@bot.message_handler(func=lambda m: m.text in ["🇲🇽 MX", "🌎 INTERNATIONAL"])
def region(m):
    regions[m.chat.id] = m.text
    send(m.chat.id, "🎧 Send your audio (max 90s preview will be generated)")

# ======================
# PRICING MENU
# ======================

def pagos(chat_id, region):

    kb = types.InlineKeyboardMarkup()

    # ======================
    # 🇲🇽 MEXICO PRICING
    # ======================

    if region == "🇲🇽 MX":

        kb.add(types.InlineKeyboardButton("PRO 1 - $450 MXN", url=PAGO_LINK))
        kb.add(types.InlineKeyboardButton("PRO 6 - $1200 MXN", url=PAGO_LINK))
        kb.add(types.InlineKeyboardButton("PRO 8 - $1600 MXN", url=PAGO_LINK))

        kb.add(types.InlineKeyboardButton("💎 PREMIUM 1 - $500 MXN", url=PAGO_LINK))
        kb.add(types.InlineKeyboardButton("💎 PREMIUM 6 - $1200 MXN", url=PAGO_LINK))
        kb.add(types.InlineKeyboardButton("💎 PREMIUM 8 - $1999 MXN", url=PAGO_LINK))

        send(chat_id, "💳 Upgrade your audio experience (Mexico pricing):", kb)

    # ======================
    # 🌎 INTERNATIONAL PRICING (ENGLISH)
    # ======================

    else:

        kb.add(types.InlineKeyboardButton("PRO 1 - $20 USD", url=PAGO_LINK))
        kb.add(types.InlineKeyboardButton("PRO 6 - $50 USD", url=PAGO_LINK))
        kb.add(types.InlineKeyboardButton("PRO 8 - $80 USD", url=PAGO_LINK))

        kb.add(types.InlineKeyboardButton("💎 PREMIUM 1 - $25 USD", url=PAGO_LINK))
        kb.add(types.InlineKeyboardButton("💎 PREMIUM 6 - $60 USD", url=PAGO_LINK))
        kb.add(types.InlineKeyboardButton("💎 PREMIUM 8 - $120 USD", url=PAGO_LINK))

        send(chat_id, "💳 Unlock full studio experience (International pricing):", kb)

# ======================
# AUDIO FLOW
# ======================

@bot.message_handler(content_types=["audio", "document"])
def audio(m):

    try:

        user_id = m.from_user.id
        region = regions.get(m.chat.id, "🌎 INTERNATIONAL")

        file_id = m.audio.file_id if m.audio else m.document.file_id
        file = bot.get_file(file_id)
        data = bot.download_file(file.file_path)

        input_file = "input.mp3"
        open(input_file, "wb").write(data)

        # ======================
        # ADMIN MODE (FULL STEMS)
        # ======================

        if is_admin(user_id):

            send(m.chat.id, "👑 ADMIN MODE - FULL STEM SEPARATION")

            subprocess.run(["demucs", input_file])

            send(m.chat.id, "🔥 STEMS GENERATED")

            return

        # ======================
        # USER MODE (90s PREVIEW)
        # ======================

        send(m.chat.id, "⚡ Processing preview...")

        subprocess.run([
            "ffmpeg", "-y",
            "-i", input_file,
            "-t", "90",
            "preview.mp3"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        subprocess.run([
            "ffmpeg", "-y",
            "-i", "preview.mp3",
            "-af", "loudnorm=I=-14:TP=-1.5",
            "final.mp3"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        bot.send_audio(
            m.chat.id,
            open("final.mp3", "rb"),
            caption="🎧 Preview ready"
        )

        pagos(m.chat.id, region)

    except Exception:
        send(m.chat.id, f"❌ ERROR:\n{traceback.format_exc()}")

# ======================
# WEBHOOK
# ======================

@app.route("/")
def home():
    return "ARSENAL ONLINE"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(
        request.get_data().decode("utf-8")
    )
    bot.process_new_updates([update])
    return "OK"

def start_webhook():
    if WEBHOOK_URL:
        bot.remove_webhook()
        bot.set_webhook(url=WEBHOOK_URL)

# ======================
# RUN
# ======================

if __name__ == "__main__":
    start_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
