import os
import telebot
import stripe
from pedalboard import Pedalboard, Compressor, Gain, HighShelfFilter, LowShelfFilter
from pedalboard.io import AudioFile
import numpy as np
from flask import Flask
from threading import Thread

# 1. CONFIGURACIÓN INICIAL (Detección de variables de entorno)
TOKEN = os.environ.get('TOKEN')
STRIPE_KEY = os.environ.get('STRIPE_KEY', 'sk_test_tu_llave_aqui') # Opcional por ahora

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# 2. SISTEMA QUIRÚRGICO DE MASTERIZACIÓN (Rack de Efectos Metal)
def masterizar_audio(input_path, output_path):
    with AudioFile(input_path) as f:
        audio = f.read(f.frames)
        samplerate = f.samplerate

    # Rack de efectos diseñado para potencia y claridad
    board = Pedalboard([
        LowShelfFilter(cutoff_frequency_hz=100, gain_db=-2), # Limpiar lodo
        HighShelfFilter(cutoff_frequency_hz=3000, gain_db=3), # Brillo metalero
        Compressor(threshold_db=-15, ratio=4),              # Control de dinámica
        Gain(gain_db=5)                                     # Volumen final
    ])

    effected = board(audio, samplerate)

    with AudioFile(output_path, 'w', samplerate, effected.shape[0]) as f:
        f.write(effected)

# 3. COMANDOS DEL BOT
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "⚡ ARSENAL BÚNKER ACTIVO ⚡\nEnvíame tu archivo de audio (.wav o .mp3) para aplicarle el proceso quirúrgico.")

@bot.message_handler(content_types=['audio', 'voice', 'document'])
def handle_audio(message):
    try:
        bot.reply_to(message, "⏳ Procesando en el búnker... espera un momento.")
        
        file_info = bot.get_file(message.audio.file_id if message.audio else message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_name = "input.wav"
        output_name = "master_arsenal.wav"
        
        with open(input_name, 'wb') as f:
            f.write(downloaded_file)
        
        # Ejecutar masterización
        masterizar_audio(input_name, output_name)
        
        # Enviar resultado
        with open(output_name, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, caption="🔥 Masterización Finalizada - Arsenal Búnker")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Error en el proceso: {str(e)}")

# 4. MANTENER EL BOT VIVO (Para Render)
@app.route('/')
def home():
    return "Arsenal Búnker está en línea."

def run_flask():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    print("🚀 Arsenal Búnker Iniciando...")
    # Iniciar Flask en un hilo separado para que Render no mate el proceso
    t = Thread(target=run_flask)
    t.start()
    # Iniciar el bot de Telegram
    bot.infinity_polling()
