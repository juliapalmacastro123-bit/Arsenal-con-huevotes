import os
import time
import telebot
from telebot import types
from flask import Flask, request
import subprocess
import shutil
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

BOT_NAME = "ARSENAL: Sound Metamorphosis"

PAGO_LINK = "https://mpago.la/2KNKzJp"

# ======================
# CHECK FFmpeg
# ======================

FFMPEG_OK = shutil.which("ffmpeg") is not None

# ======================
# SAFE SEND
# ======================

def send(chat_id, text, kb=None):
    try:
        bot.send_message(chat_id, text, reply_markup=kb)
    except Exception as e:
        print("SEND ERROR:", e)

# ======================
# REGIONES
# ======================

regions = {}

# ======================
# START
# ======================

@bot.message_handler(commands=["start"])
def start(m):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🇲🇽 MX", "🌎 INTERNATIONAL")

    send(
        m.chat.id,
        "🎧 ARSENAL ACTIVO\nManda tu demo 🔥",
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
# PAGOS
# ======================

def pagos(chat_id):
    kb = types.InlineKeyboardMarkup()

    kb.add(types.InlineKeyboardButton("⚡ 1 Track $20", url=PAGO_LINK))
    kb.add(types.InlineKeyboardButton("⚡ 6 Tracks $50", url=PAGO_LINK))
    kb.add(types.InlineKeyboardButton("⚡ 8 Tracks $80", url=PAGO_LINK))

    kb.add(types.InlineKeyboardButton("💎 PRO Upgrade", url=PAGO_LINK))

    send(chat_id, "💳 Mejora tu sonido 🔥", kb)

# ======================
# AUDIO ENGINE
# ======================

@bot.message_handler(content_types=["audio", "document"])
def audio(m):

    try:
        send(m.chat.id, "⚡ Procesando ARSENAL...")

        file_id = m.audio.file_id if m.audio else m.document.file_id
        file = bot.get_file(file_id)
        data = bot.download_file(file.file_path)

        input_file = "input_audio"
        open(input_file, "wb").write(data)

        if not FFMPEG_OK:
            send(m.chat.id, "❌ FFmpeg no instalado en servidor")
            return

        # recorte 90s
        subprocess.run([
            "ffmpeg", "-y",
            "-i", input_file,
            "-t", "90",
            "temp.mp3"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # master simple seguro
        subprocess.run([
            "ffmpeg", "-y",
            "-i", "temp.mp3",
            "-af", "loudnorm=I=-14:TP=-1.5",
            "final.mp3"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        send(m.chat.id, "🎧 Aquí tu preview mejorado")

        bot.send_audio(
            m.chat.id,
            open("final.mp3", "rb")
        )

        pagos(m.chat.id)

    except Exception:
        err = traceback.format_exc()
        send(m.chat.id, f"❌ ERROR:\n{err}")

# ======================
# WEBHOOK
# ======================

@app.route("/")
def home():
    return f"{BOT_NAME} ONLINE"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        update = telebot.types.Update.de_json(
            request.get_data().decode("utf-8")
        )
        bot.process_new_updates([update])
    except Exception as e:
        print("WEBHOOK ERROR:", e)

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
