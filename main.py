import os
import telebot
import stripe
import time
from telebot import types
from flask import Flask
from pydub import AudioSegment
from pedalboard import (
    Pedalboard, Compressor, Gain, 
    HighShelfFilter, LowShelfFilter, 
    Distortion, Limiter
)
from pedalboard.io import AudioFile

# --- CONFIGURACIÓN DE NÚCLEO ---
TOKEN = os.getenv("TOKEN")
STRIPE_KEY = os.getenv("STRIPE_KEY")
MI_LLAVE = 7949397943 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
stripe.api_key = STRIPE_KEY

# Limpieza técnica para evitar errores de conexión (409 Conflict)
bot.remove_webhook()
time.sleep(1)

# --- CATÁLOGO DE VENTAS (Tus Precios Definidos) ---
CATALOGO = {
    "cortadora": "Cortadora Rotte (Restaurada): $800 - $1,200 MXN.",
    "mazo": "Mazo de acero (Pulido): $400 - $600 MXN.",
    "pulsera": "Pulsera Tiffany & Co (Original): $3,500 - $4,500 MXN.",
    "calentador": "Calentador portátil: $500 - $700 MXN."
}

# --- INGENIERÍA DE SONIDO (PEDALBOARD) ---
def procesar_master(input_p, output_p):
    with AudioFile(input_p) as f:
        audio = f.read(f.frames)
        samplerate = f.samplerate
    board = Pedalboard([
        Compressor(threshold_db=-16, ratio=4),
        Distortion(drive_db=8),
        LowShelfFilter(cutoff_frequency_hz=200, gain_db=3),
        Limiter(threshold_db=-0.1)
    ])
    effected = board(audio, samplerate)
    with AudioFile(output_p, 'w', samplerate, effected.shape[0]) as f:
        f.write(effected)

# --- MENÚ Y COMANDOS ---
@bot.message_handler(commands=['start'])
def inicio(message):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add(
        '💀 THRASH METAL', '🩸 DEATH METAL', '☣️ GRINDCORE',
        '👊 HARDCORE', '🎸 HEAVY METAL', '🎤 ROCK URBANO',
        '🏁 SKA', '🤘 PUNK', '💰 TARIFAS / PRECIOS'
    )
    bot.send_message(message.chat.id, "🚀 **ARSENAL: SOUND METAMORPHOSIS**\nIngeniería y Ventas en un solo lugar.", reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda m: 'TARIFAS' in m.text or 'PRECIOS' in m.text)
def ver_precios(message):
    texto = "💰 **LISTA DEL ARSENAL:**\n\n"
    for item, info in CATALOGO.items(): texto += f"• {info}\n"
    texto += "\n✨ **PROCESAMIENTO:** 1 Rola $200 | 6 por $500"
    bot.reply_to(message, texto)

# --- PROCESAMIENTO QUIRÚRGICO DE AUDIO ---
@bot.message_handler(content_types=['audio', 'document'])
def handle_audio(message):
    bot.reply_to(message, "⚡ **METAMORFOSIS ACTIVADA...**")
    try:
        file_id = message.audio.file_id if message.audio else message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)
        with open("in.wav", "wb") as f: f.write(downloaded)
        
        procesar_master("in.wav", "out.wav")
        
        # Prueba de 90 segundos a 320kbps
        sound = AudioSegment.from_file("out.wav")
        final = sound[:90000]
        final.export("arsenal.mp3", format="mp3", bitrate="320k")
        
        with open("arsenal.mp3", "rb") as f:
            bot.send_audio(message.chat.id, f, caption="✨ **METAMORFOSIS LOGRADA.**")
    except:
        bot.reply_to(message, "⚠️ Error en la maquinaria.")

if __name__ == "__main__":
    print("El Arsenal está rugiendo...")
    bot.infinity_polling(timeout=20)
