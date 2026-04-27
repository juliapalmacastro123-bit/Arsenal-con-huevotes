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
if not TOKEN:
    raise ValueError("Falta TOKEN")

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
# ADMIN CHECK
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
        "🎧 <b>ARSENAL AUDIO</b>\n\nSelecciona tu región:",
        kb
    )

# ======================
# REGION
# ======================

@bot.message_handler(func=lambda m: m.text in ["🇲🇽 MX", "🌎 INTERNATIONAL"])
def region(m):
    regions[m.chat.id] = m.text
    send(m.chat.id, "🎧 Envía tu audio (máx 90s)")

# ======================
# PAYMENTS
# ======================

def pagos(chat_id, region):

    kb = types.InlineKeyboardMarkup()

    # ======================
    # 🇲🇽 MX
    # ======================

    if region == "🇲🇽 MX":

        kb.add(types.InlineKeyboardButton("PRO 1 - $450 MXN", url=PAGO_LINK))
        kb.add(types.InlineKeyboardButton("PRO 6 - $1200 MXN", url=PAGO_LINK))
        kb.add(types.InlineKeyboardButton("PRO 8 - $1600 MXN", url=PAGO_LINK))

        kb.add(types.InlineKeyboardButton("💎 PREMIUM 1 - $500 MXN", url=PAGO_LINK))
        kb.add(types.InlineKeyboardButton("💎 PREMIUM 6 - $1200 MXN", url=PAGO_LINK))
        kb.add(types.InlineKeyboardButton("💎 PREMIUM 8 - $1999 MXN", url=PAGO_LINK))

    # ======================
    # 🌎 INTERNATIONAL
    # ======================

    else:

        kb.add(types.InlineKeyboardButton("PRO 1 - $20 USD", url=PAGO_LINK))
        kb.add(types.InlineKeyboardButton("PRO 6 - $50 USD", url=PAGO_LINK))
        kb.add(types.InlineKeyboardButton("PRO 8 - $80 USD", url=PAGO_LINK))

        kb.add(types.InlineKeyboardButton("💎 PREMIUM 1 - $25 USD", url=PAGO_LINK))
        kb.add(types.InlineKeyboardButton("💎 PREMIUM 6 - $60 USD", url=PAGO_LINK))
        kb.add(types.InlineKeyboardButton("💎 PREMIUM 8 - $120 USD", url=PAGO_LINK))

    send(chat_id, "💳 Desbloquea versión completa:", kb)

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

            send(m.chat.id, "👑 ADMIN MODE - STEMS ACTIVADOS")

            subprocess.run(["demucs", input_file])

            send(m.chat.id, "🔥 STEMS GENERADOS (ADMIN)")

            return

        # ======================
        # USER MODE (PREVIEW 90s)
        # ======================

        send(m.chat.id, "⚡ Procesando preview...")

        subprocess.run([
            "ffmpeg", "-y",
            "-i", input_file,
            "-t", "90",
            "preview.mp3"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        subprocess.run([
            "ffmpeg", "-y",
            "-i", "preview
