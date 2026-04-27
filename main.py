""" ARSENAL - BACKEND UNIFICADO (PRODUCCIÓN) Flask + Telegram Bot + Audio Processing (pydub) Listo para Render / producción estable """

import os import threading import logging from flask import Flask, request, jsonify import telebot from pydub import AudioSegment

=========================

CONFIG

=========================

TOKEN = os.getenv("TOKEN") if not TOKEN: raise ValueError("Falta TOKEN en variables de entorno")

Logging básico producción

logging.basicConfig(level=logging.INFO)

Flask app

app = Flask(name)

Telegram bot

bot = telebot.TeleBot(TOKEN, parse_mode=None)

=========================

FLASK ROUTES

=========================

@app.route("/") def home(): return "ARSENAL ONLINE"

@app.route("/health") def health(): return jsonify({"status": "ok"})

Webhook opcional (si decides usarlo)

@app.route(f"/{TOKEN}", methods=["POST"]) def telegram_webhook(): json_str = request.get_data().decode("UTF-8") update = telebot.types.Update.de_json(json_str) bot.process_new_updates([update]) return "ok"

=========================

AUDIO PROCESSING

=========================

def process_audio(file_path): """ Procesamiento base seguro """ try: audio = AudioSegment.from_file(file_path)

# Ejemplo básico: normalización ligera
    audio = audio + 5

    output_path = file_path.replace(".mp3", "_processed.mp3")
    audio.export(output_path, format="mp3")

    return output_path

except Exception as e:
    logging.error(f"Error procesando audio: {e}")
    return None

=========================

TELEGRAM BOT HANDLERS

=========================

@bot.message_handler(commands=['start']) def start(message): bot.reply_to(message, "ARSENAL ONLINE - Envía tu audio para procesar")

@bot.message_handler(content_types=['audio', 'voice']) def handle_audio(message): try: file_info = bot.get_file(message.audio.file_id if message.content_type == 'audio' else message.voice.file_id) downloaded_file = bot.download_file(file_info.file_path)

input_path = "input_audio.ogg"
    with open(input_path, 'wb') as f:
        f.write(downloaded_file)

    output = process_audio(input_path)

    if output:
        with open(output, 'rb') as f:
            bot.send_audio(message.chat.id, f)
    else:
        bot.reply_to(message, "Error procesando audio")

except Exception as e:
    logging.error(e)
    bot.reply_to(message, "Error interno procesando audio")

=========================

THREAD BOT

=========================

def run_bot(): logging.info("Bot iniciado") bot.infinity_polling(skip_pending=True)

=========================

MAIN

=========================

if name == "main":

# Bot en hilo separado
t = threading.Thread(target=run_bot)
t.daemon = True
t.start()

# Flask server (producción con gunicorn recomendado)
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
