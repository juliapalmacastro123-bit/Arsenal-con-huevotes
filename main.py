import os
import time
import telebot
from telebot import types
from flask import Flask, request
import subprocess

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

BOT_NAME = "ARSENAL: La Metamorfosis del Sonido"

PRIVACY = f"""
🔒 <b>{BOT_NAME}</b>

- No almacenamos audio
- Solo se procesa temporalmente
- Se elimina automáticamente
"""

ADMIN_ID = 7949397943
vip_users = set()

def is_vip(uid):
    return uid == ADMIN_ID or uid in vip_users

# ======================
# ANTI SPAM
# ======================

last_time = {}

def anti_spam(uid):
    now = time.time()
    if now - last_time.get(uid, 0) < 8:
        return False
    last_time[uid] = now
    return True

# ======================
# REGIONES / PAGOS
# ======================

regions = {}

LINKS = {
    "MX_1": "https://mpago.la/2dMaFNh",
    "MX_6": "PON_LINK_500",
    "MX_8": "PON_LINK_850",
    "US_1": "PON_LINK_20",
    "US_6": "PON_LINK_50",
    "US_8": "PON_LINK_80"
}

def is_int(chat_id):
    return "INTERNACIONAL" in regions.get(chat_id, "")

def pagos(chat_id):
    kb = types.InlineKeyboardMarkup()

    if is_int(chat_id):
        kb.add(types.InlineKeyboardButton("1 Track $20", url=LINKS["US_1"]))
        kb.add(types.InlineKeyboardButton("6 Tracks $50", url=LINKS["US_6"]))
        kb.add(types.InlineKeyboardButton("8 Tracks $80", url=LINKS["US_8"]))
    else:
        kb.add(types.InlineKeyboardButton("1 Rola $200", url=LINKS["MX_1"]))
        kb.add(types.InlineKeyboardButton("6 Rolas $500", url=LINKS["MX_6"]))
        kb.add(types.InlineKeyboardButton("8 Rolas $850", url=LINKS["MX_8"]))

    bot.send_message(chat_id, "💳 Desbloquea versión PRO 🔥", reply_markup=kb)

# ======================
# LIMPIEZA
# ======================

def clean():
    for f in ["input.ogg", "temp.wav", "output.mp3"]:
        if os.path.exists(f):
            os.remove(f)

# ======================
# 🎛️ ARSENAL MASTER ENGINE
# ======================

def master(inp, out):
    subprocess.run([
        "ffmpeg", "-y",
        "-i", inp,

        "-af",
        (
            "highpass=f=30,"
            "lowpass=f=18000,"

            "equalizer=f=250:width_type=h:width=200:g=-2,"
            "equalizer=f=3500:width_type=h:width=300:g=2,"

            "equalizer=f=8000:width_type=h:width=4000:g=-2,"
            "equalizer=f=12000:width_type=h:width=5000:g=-1,"

            "equalizer=f=150:width_type=h:width=100:g=2,"
            "equalizer=f=4000:width_type=h:width=200:g=2,"
            "equalizer=f=9000:width_type=h:width=300:g=1,"

            "acompressor=threshold=-18dB:ratio=3:attack=5:release=80,"

            "loudnorm=I=-14:TP=-1.0:LRA=11"
        ),

        "-b:a", "320k",
        out
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ======================
# WEBHOOK
# ======================

@app.route("/")
def home():
    return f"{BOT_NAME} activo"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK"

def start_webhook():
    if WEBHOOK_URL:
        bot.remove_webhook()
        bot.set_webhook(url=WEBHOOK_URL)
        print("Webhook activo:", WEBHOOK_URL)

# ======================
# BOT
# ======================

@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(m.chat.id, PRIVACY)

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🇲🇽 MX / LATAM", "🌎 INTERNACIONAL")

    bot.send_message(
        m.chat.id,
        f"🎸 <b>{BOT_NAME}</b>\nSube tu demo 🔥",
        reply_markup=kb
    )

@bot.message_handler(func=lambda m: m.text in ["🇲🇽 MX / LATAM", "🌎 INTERNACIONAL"])
def region(m):
    regions[m.chat.id] = m.text
    bot.send_message(m.chat.id, "🎧 Envía tu audio (90s preview)")

# ======================
# AUDIO HANDLER (FIXED)
# ======================

@bot.message_handler(content_types=["audio", "document"])
def audio(m):

    if not anti_spam(m.from_user.id):
        bot.reply_to(m, "⛔ Espera unos segundos")
        return

    bot.reply_to(m, "⚡ Procesando ARSENAL...")

    try:
        fid = m.audio.file_id if m.audio else m.document.file_id
        f = bot.get_file(fid)
        data = bot.download_file(f.file_path)

        # ✅ CORRECTO: guardar como OGG original
        with open("input.ogg", "wb") as file:
            file.write(data)

        # 🔥 conversión segura a WAV real
        subprocess.run([
            "ffmpeg", "-y",
            "-i", "input.ogg",
            "-ar", "44100",
            "-ac", "2",
            "temp.wav"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if not os.path.exists("temp.wav"):
            raise Exception("FFmpeg no generó temp.wav")

        master("temp.wav", "output.mp3")

        bot.send_audio(
            m.chat.id,
            open("output.mp3", "rb"),
            caption="🎧 ARSENAL PRE-MASTER"
        )

        if not is_vip(m.from_user.id):
            pagos(m.chat.id)

        clean()

    except Exception as e:
        print("ERROR REAL:", e)
        bot.reply_to(m, f"❌ Error procesando audio:\n{e}")
        clean()

# ======================
# RUN
# ======================

if __name__ == "__main__":
    start_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
