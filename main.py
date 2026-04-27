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

ADMIN_ID = 7949397943

# ======================
# STATE
# ======================

users = {}        # {uid: {region, file}}
paid_users = set()

# ======================
# ADMIN
# ======================

def is_admin(uid):
    return int(uid) == ADMIN_ID

# ======================
# SAFE SEND
# ======================

def send(chat_id, text, kb=None):
    try:
        bot.send_message(chat_id, text, reply_markup=kb)
    except:
        pass

# ======================
# START
# ======================

@bot.message_handler(commands=["start"])
def start(m):

    users[m.chat.id] = {"region": None, "file": None}

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🇲🇽 MX", "🌎 INTERNATIONAL")

    send(m.chat.id, "🎧 ARSENAL AUDIO SYSTEM\nSelecciona tu región:", kb)

# ======================
# REGION
# ======================

@bot.message_handler(func=lambda m: m.text in ["🇲🇽 MX", "🌎 INTERNATIONAL"])
def region(m):
    users[m.chat.id]["region"] = m.text
    send(m.chat.id, "🎧 Envía tu audio (máx 90s preview)")

# ======================
# PAY MENU
# ======================

def payment_menu(chat_id, region, uid):

    kb = types.InlineKeyboardMarkup()

    if region == "🇲🇽 MX":

        kb.add(types.InlineKeyboardButton("PRO 8 - $1600 MXN", url="https://mpago.la/2KNKzJp"))
        kb.add(types.InlineKeyboardButton("PREMIUM 8 - $1600 MXN", url="https://mpago.la/2KNKzJp"))

    else:

        kb.add(types.InlineKeyboardButton("PRO 8 - $80 USD", url="https://mpago.la/2KNKzJp"))
        kb.add(types.InlineKeyboardButton("PREMIUM 8 - $120 USD", url="https://mpago.la/2KNKzJp"))

    send(chat_id, "💳 Upgrade your audio:", kb)

# ======================
# AUDIO FLOW
# ======================

@bot.message_handler(content_types=["audio", "document"])
def audio(m):

    try:

        uid = m.from_user.id
        region = users.get(uid, {}).get("region", "🌎 INTERNATIONAL")

        file_id = m.audio.file_id if m.audio else m.document.file_id
        file = bot.get_file(file_id)
        data = bot.download_file(file.file_path)

        input_file = f"{uid}.mp3"
        open(input_file, "wb").write(data)

        users[uid]["file"] = input_file

        # ======================
        # ADMIN
        # ======================

        if is_admin(uid):
            send(m.chat.id, "👑 ADMIN MODE")
            subprocess.run(["demucs", input_file])
            send(m.chat.id, "🔥 STEMS READY")
            return

        # ======================
        # FREE USERS
        # ======================

        if uid not in paid_users:

            send(m.chat.id, "⚡ Processing preview...")

            subprocess.run([
                "ffmpeg", "-y",
                "-i", input_file,
                "-t", "90",
                "preview.mp3"
            ])

            subprocess.run([
                "ffmpeg", "-y",
                "-i", "preview.mp3",
                "-af", "loudnorm=I=-14:TP=-1.5",
                "final.mp3"
            ])

            bot.send_audio(m.chat.id, open("final.mp3", "rb"))

            payment_menu(m.chat.id, region, uid)
            return

        # ======================
        # PREMIUM AUTO
        # ======================

        send(m.chat.id, "💎 Processing PREMIUM...")

        subprocess.run(["demucs", input_file])

        send(m.chat.id, "🔥 STEMS DELIVERED")

    except Exception:
        send(m.chat.id, traceback.format_exc())

# ======================
# PAYMENT WEBHOOK
# ======================

@app.route("/payment", methods=["POST"])
def payment():

    try:

        data = request.json
        ref = data.get("external_reference", "")
        status = data.get("status", "")

        if status == "approved" and ref:

            uid = int(ref.split("-")[0])
            paid_users.add(uid)

            send(uid, "💎 PAYMENT CONFIRMED")

            file = users.get(uid, {}).get("file")

            if file:
                subprocess.run(["demucs", file])
                send(uid, "🔥 PREMIUM READY")

    except Exception as e:
        print(e)

    return "OK"

# ======================
# TELEGRAM WEBHOOK
# ======================

@app.route("/")
def home():
    return "ARSENAL ONLINE"

@app.route(f"/{TOKEN}", methods=["POST"])
def telegram():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK"

# ======================
# RUN
# ======================

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
