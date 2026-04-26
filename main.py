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

# ======================
# PRIVACIDAD
# ======================

PRIVACY = f"""
🔒 <b>{BOT_NAME}</b>

- No almacenamos audio
- Solo se procesa temporalmente
- Se elimina automáticamente
"""

# ======================
# ADMIN
# ======================

ADMIN_ID = 7949397943

def is_vip(uid):
    return uid == ADMIN_ID

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
    "MX_6": "https://mpago.la/TU_LINK_500",
    "MX_8": "https://mpago.la/TU_LINK_850",

    "PRO_1": "https://mpago.la/TU_LINK_450",
    "PRO_6": "https://mpago.la/TU_LINK_1200",
    "PRO_8": "https://mpago.la/TU_LINK_1600"
}

def pagos(chat_id):

    kb = types.InlineKeyboardMarkup()

    kb.add(types.InlineKeyboardButton("⚡ 1 Rola $200", url=LINKS["MX_1"]))
    kb.add(types.InlineKeyboardButton("⚡ 6 Rolas $500", url=LINKS["MX_6"]))
    kb.add(types.InlineKeyboardButton("⚡ 8 Rolas $850", url=LINKS["MX_8"]))

    kb.add(types.InlineKeyboardButton("💎 PRO 1 Rola $450", url=LINKS["PRO_1"]))
    kb.add(types.InlineKeyboardButton("💎 PRO 6 Rolas $1200", url=LINKS["PRO_6"]))
    kb.add(types.InlineKeyboardButton("💎 PRO 8 Rolas $1600", url=LINKS["PRO_8"]))

    bot.send_message(chat_id, "💳 Elige tu mejora 🔥", reply_markup=kb)

# ======================
# LIMPIEZA
# ======================

def clean():
    for f in ["input.wav", "temp.wav", "output.mp3", "preview.mp3"]:
        if os.path.exists(f):
            os.remove(f)

# ======================
# MASTER ENGINE
# ======================

def master(inp, out):
    subprocess.run([
        "ffmpeg", "-y",
        "-i", inp,
        "-af",
        (
            "highpass=f=35,"
            "lowpass=f=18000,"

            "equalizer=f=2500:width_type=h:width=600:g=2,"
            "equalizer=f=4500:width_type=h:width=800:g=2,"

            "equalizer=f=8000:width_type=h:width=4000:g=-3,"
            "equalizer=f=12000:width_type=h:width=5000:g=-2,"

            "equalizer=f=150:width_type=h:width=100:g=2,"
            "equalizer=f=4000:width_type=h:width=200:g=2,"

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
    kb.add("🔥 EMPEZAR")

    bot.send_message(
        m.chat.id,
        f"🎸 <b>{BOT_NAME}</b>\nSube tu demo 🔥",
        reply_markup=kb
    )

@bot.message_handler(func=lambda m: m.text == "🔥 EMPEZAR")
def start2(m):
    bot.send_message(m.chat.id, "🎧 Envía tu audio (preview 90s)")

# ======================
# AUDIO
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

        open("input.wav", "wb").write(data)

        subprocess.run([
            "ffmpeg", "-y",
            "-i", "input.wav",
            "-t", "90",
            "temp.wav"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        master("temp.wav", "output.mp3")

        subprocess.run([
            "ffmpeg", "-y",
            "-i", "output.mp3",
            "-t", "90",
            "preview.mp3"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if is_vip(m.from_user.id):

            bot.send_audio(
                m.chat.id,
                open("output.mp3", "rb"),
                caption="🎧 ARSENAL FULL (ADMIN)"
            )

        else:

            msg = bot.send_audio(
                m.chat.id,
                open("preview.mp3", "rb"),
                caption=(
                    "🎧 Preview ARSENAL (90s)\n\n"
                    "🔥 Esto ya suena mejor...\n"
                    "💎 Con PRO (stems) suena aún más limpio\n\n"
                    "⏳ Se eliminará en breve"
                )
            )

            pagos(m.chat.id)

            time.sleep(70)
            try:
                bot.delete_message(m.chat.id, msg.message_id)
            except:
                pass

        clean()

    except Exception as e:
        bot.reply_to(m.chat.id, f"❌ Error:\n{str(e)}")
        clean()

# ======================
# RUN
# ======================

if __name__ == "__main__":
    start_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
