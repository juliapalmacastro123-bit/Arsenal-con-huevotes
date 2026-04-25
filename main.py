import os
import time
import telebot
from telebot import types
from pydub import AudioSegment
import subprocess
from flask import Flask, request

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

# ======================
# IDENTIDAD
# ======================

BOT_NAME = "ARSENAL: La Metamorfosis del Sonido"

PRIVACY_MSG = f"""
🔒 <b>{BOT_NAME}</b>

- Tu audio NO se almacena
- Se procesa solo para masterización
- Se elimina automáticamente
- No se comparte con terceros
"""

# ======================
# ADMIN / VIP
# ======================

ADMIN_ID = 7949397943
vip_users = set()

def es_vip(user_id):
    return user_id in vip_users or user_id == ADMIN_ID

# ======================
# SEGURIDAD
# ======================

user_last_request = {}

def anti_spam(user_id):
    now = time.time()
    last = user_last_request.get(user_id, 0)

    if now - last < 8:
        return False

    user_last_request[user_id] = now
    return True

# ======================
# REGIONES + PAGOS
# ======================

region_usuario = {}

LINKS = {
    "MX_1": "https://mpago.la/2dMaFNh",
    "MX_6": "PON_LINK_500",
    "MX_8": "PON_LINK_850",
    "US_1": "PON_LINK_20",
    "US_6": "PON_LINK_50",
    "US_8": "PON_LINK_80"
}

def es_internacional(chat_id):
    return "INTERNACIONAL" in region_usuario.get(chat_id, "")

def pagos(chat_id):
    kb = types.InlineKeyboardMarkup()

    if es_internacional(chat_id):
        kb.add(types.InlineKeyboardButton("🔥 1 Track $20 USD", url=LINKS["US_1"]))
        kb.add(types.InlineKeyboardButton("⚡ 6 Tracks $50 USD", url=LINKS["US_6"]))
        kb.add(types.InlineKeyboardButton("👑 8 Tracks $80 USD", url=LINKS["US_8"]))
    else:
        kb.add(types.InlineKeyboardButton("🔥 1 Rola $200 MXN", url=LINKS["MX_1"]))
        kb.add(types.InlineKeyboardButton("⚡ 6 Rolas $500 MXN", url=LINKS["MX_6"]))
        kb.add(types.InlineKeyboardButton("👑 8 Rolas $850 MXN", url=LINKS["MX_8"]))

    bot.send_message(chat_id,
        "💳 <b>Desbloquea tu masterización PRO</b>\n"
        "ARSENAL transforma tu demo en sonido de estudio 🔥",
        reply_markup=kb
    )

# ======================
# AUDIO ENGINE (METAL FOCUSED)
# ======================

def purgar():
    for f in ["input.wav", "temp.wav", "output.mp3"]:
        if os.path.exists(f):
            os.remove(f)

def masterizar(inp, out):
    filtro = "loudnorm=I=-8,compressor"

    subprocess.run([
        "ffmpeg", "-y", "-i", inp,
        "-af", filtro,
        "-b:a", "320k",
        out
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ======================
# FLASK WEBHOOK
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
# BOT FLOW
# ======================

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, PRIVACY_MSG)

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🇲🇽 MX / LATAM", "🌎 INTERNACIONAL")

    bot.send_message(m.chat.id,
        f"🎸 <b>{BOT_NAME}</b>\n"
        "Sube tu demo y conviértelo en sonido de estudio 🔥",
        reply_markup=kb
    )

@bot.message_handler(func=lambda m: m.text in ["🇲🇽 MX / LATAM", "🌎 INTERNACIONAL"])
def region(m):
    region_usuario[m.chat.id] = m.text
    bot.send_message(m.chat.id, "🎧 Envía tu audio (máx 90s preview)")

@bot.message_handler(content_types=['audio','document'])
def audio(m):

    if not anti_spam(m.from_user.id):
        bot.reply_to(m, "⛔ Espera unos segundos")
        return

    bot.reply_to(m, "⚡ Procesando...")

    try:
        fid = m.audio.file_id if m.audio else m.document.file_id
        f = bot.get_file(fid)
        data = bot.download_file(f.file_path)

        open("input.wav", "wb").write(data)

        AudioSegment.from_file("input.wav")[:90000].export("temp.wav", format="wav")

        masterizar("temp.wav", "output.mp3")

        bot.send_audio(m.chat.id, open("output.mp3", "rb"), caption="🎧 Preview ARSENAL")

        if es_vip(m.from_user.id):
            bot.send_message(m.chat.id, "👑 VIP activo")
        else:
            pagos(m.chat.id)

        purgar()

    except:
        bot.reply_to(m, "❌ Error en procesamiento")
        purgar()

# ======================
# START
# ======================

if __name__ == "__main__":
    start_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
