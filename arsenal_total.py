import os
import telebot
from telebot import types
from pydub import AudioSegment
import subprocess

# =========================
# CONFIG
# =========================
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

MI_LLAVE = 7949397943  # tu ID VIP

# LINKS DE PAGO (EDITA LOS FALTANTES)
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

# =========================
# LIMPIEZA (NO GUARDAS NADA)
# =========================
def purgar():
    for f in ["input.wav", "temp.wav", "output.mp3"]:
        if os.path.exists(f):
            os.remove(f)

# =========================
# UTIL
# =========================
def es_internacional(chat_id):
    return "INTERNACIONAL" in region_usuario.get(chat_id, "")

# =========================
# ANUNCIO
# =========================
def anuncio(chat_id):
    if es_internacional(chat_id):
        return (
            "🔥 ARSENAL: SOUND METAMORPHOSIS 🔥\n\n"
            "Turn your rough demo into a powerful, clean track.\n\n"
            "• Loud • Clear • Punchy\n\n"
            "🧪 FREE 90s preview\n\n"
            "🔒 Your music is processed and deleted automatically."
        )
    else:
        return (
            "🔥 ARSENAL: SOUND METAMORPHOSIS 🔥\n\n"
            "Convierte tu demo en un track potente y limpio.\n\n"
            "• Más volumen • Más claridad • Más punch\n\n"
            "🧪 Prueba gratis (90s)\n\n"
            "🔒 Tu música no se guarda. Se elimina automáticamente."
        )

# =========================
# GENERO
# =========================
def detectar_genero(texto):
    texto = texto.lower()
    if any(x in texto for x in ["thrash","death","black","grind"]):
        return "EXTREMO"
    elif any(x in texto for x in ["heavy","hard rock"]):
        return "CLASICO"
    elif any(x in texto for x in ["punk","hardcore"]):
        return "PUNK"
    elif any(x in texto for x in ["urbano","latino"]):
        return "URBANO"
    elif any(x in texto for x in ["indie","post"]):
        return "INDIE"
    elif "ska" in texto:
        return "SKA"
    return "CLASICO"

# =========================
# MASTER AUDIO
# =========================
def masterizar(input_path, output_path, perfil):
    perfiles = {
        "EXTREMO": "equalizer=f=120:g=-4,equalizer=f=3000:g=4,acompressor=threshold=-20dB:ratio=3,loudnorm=I=-8:TP=-1.5",
        "CLASICO": "equalizer=f=200:g=2,equalizer=f=4000:g=2,acompressor=threshold=-18dB:ratio=2,loudnorm=I=-10:TP=-1.5",
        "PUNK": "equalizer=f=150:g=-2,equalizer=f=3500:g=5,acompressor=threshold=-22dB:ratio=4,loudnorm=I=-7:TP=-1.5",
        "URBANO": "equalizer=f=100:g=1,equalizer=f=3000:g=3,acompressor=threshold=-18dB:ratio=2,loudnorm=I=-9:TP=-1.5",
        "INDIE": "equalizer=f=120:g=-1,equalizer=f=8000:g=3,acompressor=threshold=-16dB:ratio=1.5,loudnorm=I=-11:TP=-1.5",
        "SKA": "equalizer=f=150:g=-3,equalizer=f=2500:g=3,acompressor=threshold=-17dB:ratio=2,loudnorm=I=-10:TP=-1.5"
    }
    filtro = perfiles.get(perfil, perfiles["CLASICO"])
    subprocess.run([
        "ffmpeg","-y","-i",input_path,
        "-af",filtro,
        "-b:a","320k",
        output_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# =========================
# START
# =========================
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇲🇽 MX / LATAM", "🌎 INTERNACIONAL")
    bot.send_message(message.chat.id, "🌍 Select your region / Selecciona tu región:", reply_markup=markup)

# =========================
# REGIÓN
# =========================
@bot.message_handler(func=lambda m: m.text in ["🇲🇽 MX / LATAM","🌎 INTERNACIONAL"])
def region(message):
    region_usuario[message.chat.id] = message.text
    bot.send_message(message.chat.id, anuncio(message.chat.id))

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=3)
    botones = [
        "💀 THRASH","🩸 DEATH","🌑 BLACK",
        "☣️ GRINDCORE","👊 HARDCORE","🎸 HEAVY",
        "🔥 HARD ROCK","🎤 URBANO","🏁 SKA",
        "🤘 PUNK","🎸 INDIE","🌫️ POST-PUNK"
    ]
    markup.add(*botones)
    bot.send_message(message.chat.id,"🎸 Elige género y manda tu audio:",reply_markup=markup)

# =========================
# GENERO
# =========================
@bot.message_handler(func=lambda m: True, content_types=['text'])
def genero(message):
    genero_usuario[message.chat.id] = message.text
    bot.reply_to(message,"🎧 Envía tu audio")

# =========================
# PAGOS
# =========================
def pagos(chat_id):
    markup = types.InlineKeyboardMarkup()

    if es_internacional(chat_id):
        markup.add(types.InlineKeyboardButton("1 Track - $20 USD", url=LINKS["US_1"]))
        markup.add(types.InlineKeyboardButton("6 Tracks - $50 USD", url=LINKS["US_6"]))
        markup.add(types.InlineKeyboardButton("8 Tracks - $80 USD", url=LINKS["US_8"]))
        bot.send_message(chat_id,"💳 Choose your package:",reply_markup=markup)
    else:
        markup.add(types.InlineKeyboardButton("1 Rola - $200 MXN", url=LINKS["MX_1"]))
        markup.add(types.InlineKeyboardButton("6 Rolas - $500 MXN", url=LINKS["MX_6"]))
        markup.add(types.InlineKeyboardButton("8 Rolas - $850 MXN", url=LINKS["MX_8"]))
        bot.send_message(chat_id,"💳 Elige tu paquete:",reply_markup=markup)

# =========================
# AUDIO
# =========================
@bot.message_handler(content_types=['audio','document'])
def audio(message):
    es_vip = (message.from_user.id == MI_LLAVE)
    bot.reply_to(message,"⚡ Procesando...")

    try:
        file_id = message.audio.file_id if message.audio else message.document.file_id
        file_info = bot.get_file(file_id)
        data = bot.download_file(file_info.file_path)

        with open("input.wav","wb") as f:
            f.write(data)

        audio = AudioSegment.from_file("input.wav")
        preview = audio[:90000]
        preview.export("temp.wav", format="wav")

        perfil = detectar_genero(genero_usuario.get(message.chat.id,"general"))
        masterizar("temp.wav","output.mp3",perfil)

        with open("output.mp3","rb") as f:
            bot.send_audio(message.chat.id,f,caption="🎧 Preview 90s")

        if es_vip:
            masterizar("input.wav","output.mp3",perfil)
            with open("output.mp3","rb") as f:
                bot.send_audio(message.chat.id,f,caption="👑 Full VIP")
        else:
            pagos(message.chat.id)

        purgar()

    except:
        bot.reply_to(message,"❌ Error")
        purgar()

# =========================
# RUN
# =========================
if __name__ == "__main__":
    print("Bot activo...")
    bot.infinity_polling()
