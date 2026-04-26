import os
import telebot
from flask import Flask, request
from pydub import AudioSegment
import tempfile

# ======================
# CONFIG
# ======================

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("Falta TOKEN")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ======================
# WEBHOOK
# ======================

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok", 200

@app.route("/")
def home():
    return "🔥 Arsenal activo"

# ======================
# FUNCIONES AUDIO
# ======================

def procesar_audio(input_path, output_path):
    audio = AudioSegment.from_file(input_path)

    # 🔥 Cadena básica (puedes tunear después)
    audio = audio.normalize()
    audio = audio + 5  # boost leve

    # Exportar
    audio.export(output_path, format="mp3")

# ======================
# TELEGRAM HANDLERS
# ======================

@bot.message_handler(content_types=["audio", "voice", "document"])
def handle_audio(message):
    try:
        bot.reply_to(message, "🔥 Procesando tu demo...")

        file_info = bot.get_file(message.audio.file_id if message.audio else message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as input_file:
            input_file.write(downloaded_file)
            input_path = input_file.name

        output_path = input_path.replace(".ogg", ".mp3")

        procesar_audio(input_path, output_path)

        with open(output_path, "rb") as f:
            bot.send_audio(message.chat.id, f)

        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# ======================
# START
# ======================

if __name__ == "__main__":
    bot.remove_webhook()

    RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
    if not RENDER_URL:
        raise ValueError("Falta RENDER_EXTERNAL_URL")

    bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")
    print(f"Webhook activo: {RENDER_URL}/{TOKEN}")

    app.run(host="0.0.0.0", port=10000)
