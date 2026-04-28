import os
import threading
import telebot
import numpy as np
from flask import Flask
from pedalboard import Pedalboard, Compressor, Gain, HighpassFilter, Limiter, Distortion, Reverb
from pedalboard.io import AudioFile

# CONFIGURACIÓN
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

def process_audio(path, is_demo=True):
    with AudioFile(path) as f:
        audio = f.read(f.frames)
        sr = f.sample_rate
    
    # Si es demo, cortamos a 90 segundos
    if is_demo:
        audio = audio[:, :int(sr * 90)]
    
    # RACK DE METAMORFOSIS PARA METAL
    board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=65),
        Compressor(threshold_db=-16, ratio=4.5),
        Distortion(drive_db=2.5),
        Reverb(room_size=0.4, wet_level=0.1),
        Gain(gain_db=2),
        Limiter(threshold_db=-0.1)
    ])
    
    mastered = board(audio, sr)
    out_path = f"/tmp/arsenal_{np.random.randint(1000)}.wav"
    with AudioFile(out_path, 'w', sr, mastered.shape[0]) as f:
        f.write(mastered)
    return out_path

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "🤘 **ARSENAL BÚNKER ACTIVO**\n\nIngeniería de sonido para Metal. Envía tu archivo de audio (WAV/MP3) y recibe una **Preview GRATIS** de 90 segundos masterizada.")

@bot.message_handler(content_types=['audio', 'document'])
def handle_docs(m):
    uid = m.chat.id
    bot.send_message(uid, "⚙️ Transformando tu sonido... espera un momento.")
    
    file_id = m.audio.file_id if m.audio else m.document.file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    input_path = f"/tmp/in_{uid}.wav"
    with open(input_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    # Procesar Demo
    demo_path = process_audio(input_path, is_demo=True)
    
    with open(demo_path, 'rb') as audio_demo:
        bot.send_audio(uid, audio_demo, caption="🎁 **Preview de 90s Lista**\n\n💰 **Costo Full Master:** $200 MXN\n🏦 **CLABE:** `722969028966531373`\n\nManda captura del pago para liberarte la rola completa.")

@app.route("/")
def index(): return "Arsenal Online"

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.infinity_polling()).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
