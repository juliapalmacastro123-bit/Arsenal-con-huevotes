""" ARSENAL - BACKEND PRODUCCIÓN FINAL ESTABLE (NO WEBHOOK / SOLO POLLING) Flask + Telegram Bot + Audio Processing (pydub) Optimizado para Render (sin conflictos de arranque)

OBJETIVO:

Cero conflicto webhook/polling

Inicio estable en Render

Procesamiento seguro de audio

Preview 90s + master completo interno """


import os import threading import logging from flask import Flask, jsonify import telebot from pydub import AudioSegment

=========================

CONFIG

=========================

TOKEN = os.getenv("TOKEN") if not TOKEN: raise ValueError("Falta TOKEN en variables de entorno")

logging.basicConfig(level=logging.INFO)

app = Flask(name) bot = telebot.TeleBot(TOKEN, parse_mode=None)

=========================

FLASK (SOLO ESTADO)

=========================

@app.route("/") def home(): return "ARSENAL ONLINE - OK"

@app.route("/health") def health(): return jsonify({"status": "ok"})

=========================

AUDIO PROCESSING SEGURO

=========================

def create_master(audio_path): try: audio = AudioSegment.from_file(audio_path) audio = audio + 5  # master simple base

output = audio_path.replace(".ogg", "_master.mp3")
    audio.export(output, format="mp3")

    return output

except Exception as e:
    logging.error(f"Error master: {e}")
    return None

def create_preview(audio_path, seconds=90): try: audio = AudioSegment.from_file(audio_path) preview = audio[:seconds * 1000]

output = audio_path.replace(".ogg", "_preview.mp3")
    preview.export(output, format="mp3")

    return output

except Exception as e:
    logging.error(f"Error preview: {e}")
    return None

=========================

BOT HANDLER

=========================

@bot.message_handler(commands=['start']) def start(message): bot.reply_to( message, "ARSENAL ONLINE 🎧\nEnvía tu audio para preview de 90s masterizado" )

@bot.message_handler(content_types=['audio', 'voice']) def handle_audio(message): try: file_id = message.audio.file_id if message.content_type == 'audio' else message.voice.file_id file_info = bot.get_file(file_id) downloaded = bot.download_file(file_info.file_path)

input_path = "/tmp/input_audio.ogg"

    with open(input_path, "wb") as f:
        f.write(downloaded)

    # MASTER (interno)
    master = create_master(input_path)

    # PREVIEW (gratis)
    preview = create_preview(master or input_path)

    if preview:
        with open(preview, "rb") as f:
            bot.send_audio(
                message.chat.id,
                f,
                caption="🎧 Preview 90s (versión gratuita)"
            )

        bot.send_message(
            message.chat.id,
            "🔒 Para versión completa contacta versión PRO"
        )
    else:
        bot.reply_to(message, "Error procesando audio")

except Exception as e:
    logging.error(e)
    bot.reply_to(message, "Error interno procesando audio")

=========================

BOT THREAD (POLLING SOLO)

=========================

def run_bot(): logging.info("Bot iniciado en polling seguro") bot.infinity_polling(skip_pending=True)

=========================

MAIN (NO WEBHOOK)

=========================

if name == "main":

# Bot en hilo separado
t = threading.Thread(target=run_bot)
t.daemon = True
t.start()

# Flask server
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
