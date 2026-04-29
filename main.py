import os
import subprocess
import sys

# --- MANIOBRA QUIRÚRGICA DE INSTALACIÓN ---
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import telebot
except ImportError:
    install_package('pyTelegramBotAPI')
    import telebot

try:
    import stripe
except ImportError:
    install_package('stripe')
    import stripe

try:
    from pedalboard import Pedalboard, Compressor, Gain, HighShelfFilter, LowShelfFilter
    from pedalboard.io import AudioFile
except ImportError:
    install_package('pedalboard')
    from pedalboard import Pedalboard, Compressor, Gain, HighShelfFilter, LowShelfFilter
    from pedalboard.io import AudioFile

import numpy as np
from flask import Flask
from threading import Thread

# --- CONFIGURACIÓN ---
TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- MOTOR DE AUDIO (RACK METAL) ---
def masterizar_audio(input_path, output_path):
    with AudioFile(input_path) as f:
        audio = f.read(f.frames)
        samplerate = f.samplerate

    board = Pedalboard([
        LowShelfFilter(cutoff_frequency_hz=100, gain_db=-2),
        HighShelfFilter(cutoff_frequency_hz=3000, gain_db=3),
        Compressor(threshold_db=-15, ratio=4),
        Gain(gain_db=5)
    ])

    effected = board(audio, samplerate)

    with AudioFile(output_path, 'w', samplerate, effected.shape[0]) as f:
        f.write(effected)

# --- COMANDOS BOT ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "⚡ ARSENAL BÚNKER ACTIVO ⚡\nEnvíame un audio para procesarlo con el rack de Metal.")

@bot.message_handler(content_types=['audio', 'document'])
def handle_audio(message):
    try:
        bot.reply_to(message, "⏳ Procesando en el búnker...")
        file_id = message.audio.file_id if message.audio else message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_name = "input.wav"
        output_name = "master_arsenal.wav"
        
        with open(input_name, 'wb') as f:
            f.write(downloaded_file)
        
        masterizar_audio(input_name, output_name)
        
        with open(output_name, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, caption="🔥 Masterizado por Arsenal Búnker")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# --- MANTENER VIVO EN RENDER ---
@app.route('/')
def home():
    return "Bunker Online"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    print("🚀 Arsenal Búnker Despegando...")
    Thread(target=run_flask).start()
    bot.infinity_polling()
