import os
import telebot
from telebot import types
from pydub import AudioSegment
import subprocess
from flask import Flask
import threading

# =======================
# CONFIG
# =======================

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("Falta TOKEN")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

MI_LLAVE = 7949397943

LINKS = {
    "MX_1": "https://mpago.la/2dMaFNh",
    "MX_6": "PON_LINK_500",
    "MX_8": "PON_LINK_850",
    "US_1": "PON_LINK_20",
    "US_6": "PON_LINK_50",
    "US_8": "PON_LINK_80"
}

region_usuario = {}
genero_usuario = {}

# =======================
# FLASK (RENDER PORT FIX)
# =======================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot activo"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# =======================
# UTILIDADES
# =======================

def purgar():
    for f in ["input.wav", "temp.wav", "output.mp3"]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except:
                pass

def es_internacional(chat_id):
    return "INTERNACIONAL" in region_usuario.get(chat_id, "")

def anuncio(chat_id):
    if es_internacional(chat_id):
        return (
            "🔥 <b>ARSENAL: SOUND METAMORPHOSIS</b> 🔥\n\n"
            "Turn your demo into a powerful track.\n\n"
            "• Loud • Clear • Punchy\n\n"
            "🧪 FREE 90s preview\n"
            "🔒 Auto-deleted audio."
        )
    else:
        return (
            "🔥 <b>ARSENAL: SOUND METAMORPHOSIS</b> 🔥\n\n"
            "Convierte tu demo en algo profesional.\n\n"
            "• Más volumen • Más claridad • Más punch\n\n"
            "🧪 Prueba gratis (90s)\n"
            "🔒 Se elimina automáticamente."
        )

def detectar_genero(t):
    t = t.lower()
    if any(x in t for x in ["thrash", "death", "black", "grind"]):
        return "EXTREMO"
    elif any(x in t for x in ["heavy", "hard rock"]):
        return "CLASICO"
    elif any(x in t for x in ["punk", "hardcore"]):
        return "PUNK"
    elif any(x in t for x in ["urbano", "latino"]):
        return "URBANO"
    elif any(x in t for x in ["indie", "post"]):
        return "INDIE"
    elif "ska" in t:
        return "SKA"
    return "CLASICO"

def masterizar(inp, out, perfil):
    filtros = {
        "EXTREMO": "loudnorm=I=-8",
        "CLASICO": "loudnorm=I=-10",
        "PUNK": "loudnorm=I=-7",
        "URBANO": "loudnorm=I=-9",
        "INDIE": "loudnorm=I=-11",
        "SKA": "loudnorm=I=-10"
    }

    f = filtros.get(perfil, "loudnorm=I=-10")

    subprocess.run([
        "ffmpeg", "-y", "-i", inp,
        "-af", f,
        "-b:a", "320k",
        out
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# =======================
# BOT HANDLERS
# =======================

@bot.message_handler(commands=['start'])
def start(m):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🇲🇽 MX / LATAM", "🌎 INTERNACIONAL")
    bot.send_message(m.chat.id, "🌍 Selecciona región:", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text in ["🇲🇽 MX / LATAM", "🌎 INTERNACIONAL"])
def region(m):
    region_usuario[m.chat.id] = m.text
    bot.send_message(m.chat.id, anuncio(m.chat.id))

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    kb.add("💀 THRASH","🩸 DEATH","🌑 BLACK",
           "☣️ GRINDCORE","👊 HARDCORE","🎸 HEAVY",
           "🔥 HARD ROCK","🎤 URBANO","🏁 SKA",
           "🤘 PUNK","🎸 INDIE","🌫️ POST-PUNK")

    bot.send_message(m.chat.id, "🎸 Elige género y manda audio", reply_markup=kb)

@bot.message_handler(func=lambda m: True, content_types=['text'])
def genero(m):
    genero_usuario[m.chat.id] = m.text
    bot.reply_to(m, "🎧 Envía tu audio")

def pagos(chat_id):
    kb = types.InlineKeyboardMarkup()

    if es_internacional(chat_id):
        kb.add(types.InlineKeyboardButton("1 Track $20", url=LINKS["US_1"]))
        kb.add(types.InlineKeyboardButton("6 Tracks $50", url=LINKS["US_6"]))
        kb.add(types.InlineKeyboardButton("8 Tracks $80", url=LINKS["US_8"]))
        bot.send_message(chat_id, "💳 Choose package:", reply_markup=kb)
    else:
        kb.add(types.InlineKeyboardButton("1 Rola $200", url=LINKS["MX_1"]))
        kb.add(types.InlineKeyboardButton("6 Rolas $500", url=LINKS["MX_6"]))
        kb.add(types.InlineKeyboardButton("8 Rolas $850", url=LINKS["MX_8"]))
        bot.send_message(chat_id, "💳 Elige paquete:", reply_markup=kb)

@bot.message_handler(content_types=['audio','document'])
def audio(m):
    es_vip = (m.from_user.id == MI_LLAVE)
    bot.reply_to(m, "⚡ Procesando...")

    try:
        fid = m.audio.file_id if m.audio else m.document.file_id
        f = bot.get_file(fid)
        data = bot.download_file(f.file_path)

        open("input.wav", "wb").write(data)

        a = AudioSegment.from_file("input.wav")
        a[:90000].export("temp.wav", format="wav")

        perfil = detectar_genero(genero_usuario.get(m.chat.id, ""))
        masterizar("temp.wav", "output.mp3", perfil)

        bot.send_audio(m.chat.id, open("output.mp3", "rb"), caption="🎧 Preview")

        if es_vip:
            masterizar("input.wav", "output.mp3", perfil)
            bot.send_audio(m.chat.id, open("output.mp3", "rb"), caption="👑 FULL")
        else:
            pagos(m.chat.id)

        purgar()

    except:
        bot.reply_to(m, "❌ Error")
        purgar()

# =======================
# FIX TELEGRAM + START
# =======================

bot.remove_webhook()

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    print("Bot activo...")
    bot.infinity_polling(skip_pending=True)
