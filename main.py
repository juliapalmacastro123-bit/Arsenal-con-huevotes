import os
import telebot
import stripe
import time
from telebot import types
from flask import Flask, request
from pydub import AudioSegment
from pedalboard import (
    Pedalboard, Compressor, Gain, 
    HighShelfFilter, LowShelfFilter, 
    Distortion, Limiter, PeakFilter
)
from pedalboard.io import AudioFile

# ======================
# CONFIGURACIÓN NÚCLEO
# ======================
TOKEN = os.environ.get('TOKEN')
STRIPE_KEY = os.environ.get('STRIPE_KEY')
MI_LLAVE = 7949397943  # Tu ID de mando

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
stripe.api_key = STRIPE_KEY

# Limpieza de Webhook para evitar conflictos en Render
bot.remove_webhook()
time.sleep(1)

# ======================
# INGENIERÍA QUIRÚRGICA (PEDALBOARD)
# ======================
def master_arsenal(input_path, output_path):
    with AudioFile(input_path) as f:
        audio = f.read(f.frames)
        samplerate = f.samplerate

    board = Pedalboard([
        Compressor(threshold_db=-18, ratio=4),
        LowShelfFilter(cutoff_frequency_hz=150, gain_db=2),
        HighShelfFilter(cutoff_frequency_hz=3000, gain_db=3),
        Distortion(drive_db=5), # El toque del Arsenal
        Gain(gain_db=1.5),
        Limiter(threshold_db=-0.1)
    ])

    effected = board(audio, samplerate)

    with AudioFile(output_path, 'w', samplerate, effected.shape[0]) as f:
        f.write(effected)

# ======================
# MENÚ DE CASILLAS Y TARIFAS
# ======================
@bot.message_handler(commands=['start'])
def inicio(message):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add(
        '💀 THRASH METAL', '🩸 DEATH METAL', '🌑 BLACK METAL',
        '☣️ GRINDCORE', '👊 HARDCORE', '🎸 HEAVY METAL',
        '🎤 ROCK URBANO', '🏁 SKA', '🤘 PUNK',
        '🎸 INDIE', '🌎 ROCK LATINO', '💰 TARIFAS'
    )
    
    msg = (
        "🚀 **ARSENAL: SOUND METAMORPHOSIS**\n"
        "⚡ *La Metamorfosis del Sonido* ⚡\n\n"
        "Ingeniería quirúrgica para tus tracks.\n"
        "✨ **PRUEBA DE 90 SEGUNDOS GRATIS**"
    )
    bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda m: 'TARIFAS' in m.text)
def tarifas(message):
    bot.reply_to(message, (
        "💰 **LOGÍSTICA DE PRECIOS:**\n\n"
        "🇲🇽 **MX:** 1 Rola: $200 | 6: $500\n"
        "🇺🇸 **USA:** 1 Song: $20 | 6: $50"
    ), parse_mode='Markdown')

# ======================
# PROCESAMIENTO MULTIMEDIA
# ======================
@bot.message_handler(content_types=['audio', 'document'])
def bunker_audio(message):
    bot.reply_to(message, "⚡ **METAMORFOSIS QUIRÚRGICA ACTIVADA...**")
    
    try:
        file_id = message.audio.file_id if message.audio else message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        with open("temp_in.wav", "wb") as f: f.write(downloaded)
        
        # Procesamiento
        master_arsenal("temp_in.wav", "temp_out.wav")
        
        # Convertir a MP3 320k con Pydub
        sound = AudioSegment.from_file("temp_out.wav")
        final = sound[:90000] # Prueba de 90 seg
        final.export("final.mp3", format="mp3", bitrate="320k")
        
        with open("final.mp3", "rb") as f:
            bot.send_audio(message.chat.id, f, caption="✨ **METAMORFOSIS LOGRADA.**")
            
    except Exception as e:
        bot.reply_to(message, "⚠️ Error técnico en el Arsenal. Revisa el formato.")

# ======================
# FLASK PARA RENDER
# ======================
@app.route('/')
def index(): return "Arsenal Online"

if __name__ == "__main__":
    print("El Arsenal está rugiendo...")
    bot.infinity_polling(timeout=20)
