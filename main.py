import os
import threading
import logging
import stripe
import requests
import numpy as np
import telebot
from flask import Flask, request, abort
from pedalboard import Pedalboard, Compressor, Gain, HighpassFilter, Limiter, Distortion, Reverb
from pedalboard.io import AudioFile

# ======================
# CONFIGURACIÓN (VARIABLES DE ENTORNO)
# ======================
TOKEN = os.getenv("TOKEN")
STRIPE_SECRET = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK = os.getenv("STRIPE_WEBHOOK_SECRET")

stripe.api_key = STRIPE_SECRET
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
sessions = {}

# ======================
# MOTOR DE AUDIO: LA METAMORFOSIS
# ======================
def process_arsenal(tracks_dict, is_demo=True):
    loaded_tracks = []
    sr = 44100
    for path in tracks_dict.values():
        with AudioFile(path) as f:
            audio = f.read(f.frames)
            sr = f.sample_rate
            loaded_tracks.append(audio)

    # Mezcla Multitrack (Suma de señales)
    min_len = min(t.shape[1] for t in loaded_tracks)
    combined = np.zeros((loaded_tracks[0].shape[0], min_len))
    for t in loaded_tracks:
        combined += t[:, :min_len]
    combined /= len(loaded_tracks)

    # Corte de 90s para la prueba gratis
    if is_demo:
        combined = combined[:, :int(sr * 90)]

    # RACK PROFESIONAL (EQ, Comp, Dist, Reverb, Gain, Limiter)
    board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=65),
        Compressor(threshold_db=-16, ratio=4.5),
        Distortion(drive_db=2.5),
        Reverb(room_size=0.4, wet_level=0.1),
        Gain(gain_db=2),
        Limiter(threshold_db=-0.1)
    ])

    mastered = board(combined, sr)
    out_path = f"/tmp/final_{np.random.randint(10000)}.wav"
    with AudioFile(out_path, 'w', sr, mastered.shape[0]) as f:
        f.write(mastered)
    return out_path

# ======================
# SEGURIDAD Y PRECIOS POR PAÍS
# ======================
def get_user_region(ip):
    try:
        # Detectamos país e IP sospechosa (VPN)
        res = requests.get(f"http://ip-api.com/json/{ip}?fields=countryCode,proxy").json()
        return res.get("countryCode", "MX"), res.get("proxy", False)
    except:
        return "MX", False

def send_price_menu(m):
    uid = m.chat.id
    # En Render, la IP viene en el header 'X-Forwarded-For'
    user_ip = request.headers.get('X-Forwarded-For', m.from_user.id)
    country, is_vpn = get_user_region(user_ip)

    markup = telebot.types.InlineKeyboardMarkup()
    
    if country == "US" or is_vpn:
        # Menú Internacional (USD)
        markup.add(telebot.types.InlineKeyboardButton("🎧 1 Song ($20 USD)", callback_data="p_usd"))
        markup.add(telebot.types.InlineKeyboardButton("🔥 PREMIUM MIX ($50 USD)", callback_data="p_usd"))
        bot.send_message(uid, "🔥 **YOUR MASTER IS READY**\nSelect your package:", reply_markup=markup)
    else:
        # Menú México (MXN)
        markup.add(telebot.types.InlineKeyboardButton("🎧 1 Rola ($200)", url="https://mpago.la/2UYcmn5"))
        markup.add(telebot.types.InlineKeyboardButton("🎧 6 Rolas ($500)", url="https://mpago.la/2EmSGm8"))
        markup.add(telebot.types.InlineKeyboardButton("🎧 8 Rolas ($850)", url="https://mpago.la/2AoqQer"))
        markup.add(telebot.types.InlineKeyboardButton("🏦 TRANSFERENCIA CLABE", callback_data="ver_clabe"))
        bot.send_message(uid, "🔥 **TU MASTER ESTÁ LISTO**\nElige tu opción de pago:", reply_markup=markup)

# ======================
# HANDLERS DEL BOT
# ======================
@bot.message_handler(commands=['start'])
def start(m):
    sessions[m.from_user.id] = {"mode": None, "tracks": {}, "step": None, "full": None}
    bot.send_message(m.chat.id, "🤘 **EL ARSENAL**\n\n1. Estándar (1 Pista)\n2. Premium (Mezcla Multitrack)\n\n*Respetamos tu arte: No guardamos copias de tu música.*")

@bot.message_handler(func=lambda m: m.text in ["1", "2"])
def set_mode(m):
    uid = m.from_user.id
    if m.text == "1":
        sessions[uid]["mode"] = "single"
        bot.send_message(m.chat.id, "🎧 Envía tu canción completa.")
    else:
        sessions[uid]["mode"] = "multi"
        sessions[uid]["step"] = "drums"
        bot.send_message(m.chat.id, "🥁 **PASO 1:** Envía la BATERÍA.")

@bot.message_handler(content_types=['audio', 'document'])
def handle_audio(m):
    uid = m.from_user.id
    s = sessions.get(uid)
    if not s: return

    file_id = m.audio.file_id if m.audio else m.document.file_id
    file_info = bot.get_file(file_id)
    data = bot.download_file(file_info.file_path)
    path = f"/tmp/{uid}_{np.random.randint(100)}.wav"
    with open(path, "wb") as f: f.write(data)

    if s["mode"] == "multi":
        s["tracks"][s["step"]] = path
        steps = ["drums", "bass", "guitar", "vocals"]
        idx = steps.index(s["step"])
        if idx < len(steps) - 1:
            s["step"] = steps[idx + 1]
            bot.send_message(uid, f"✅ Recibido. Ahora envía: **{s['step'].upper()}**")
        else:
            bot.send_message(uid, "⚙️ Masterizando mezcla multitrack...")
            demo = process_arsenal(s["tracks"], is_demo=True)
            s["full"] = process_arsenal(s["tracks"], is_demo=False)
            with open(demo, "rb") as d: bot.send_audio(uid, d, caption="🎁 Prueba Premium (90s)")
            send_price_menu(m)
    else:
        demo = process_arsenal({"m": path}, is_demo=True)
        s["full"] = process_arsenal({"m": path}, is_demo=False)
        with open(demo, "rb") as d: bot.send_audio(uid, d, caption="🎁 Prueba Estándar (90s)")
        send_price_menu(m)

@bot.callback_query_handler(func=lambda call: call.data == "ver_clabe")
def clabe(call):
    bot.send_message(call.message.chat.id, "🏦 **CLABE:** `722969028966531373`\nEnvía tu comprobante para recibir el archivo completo.")

# ======================
# INICIO
# ======================
if __name__ == "__main__":
    threading.Thread(target=lambda: bot.infinity_polling()).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
