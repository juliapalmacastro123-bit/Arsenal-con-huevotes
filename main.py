import os
import telebot
import stripe
from telebot import types
from pedalboard import Pedalboard, Compressor, Gain, HighShelfFilter, LowShelfFilter
from pedalboard.io import AudioFile
from flask import Flask, request
from threading import Thread
from pydub import AudioSegment

# ======================
# CONFIG
# ======================

TOKEN = os.environ.get('TOKEN')
STRIPE_KEY = os.environ.get('STRIPE_KEY')
BOT_USERNAME = os.environ.get('BOT_USERNAME')  # sin @

if not TOKEN or not STRIPE_KEY or not BOT_USERNAME:
    raise ValueError("Faltan variables de entorno")

bot = telebot.TeleBot(TOKEN)
stripe.api_key = STRIPE_KEY
app = Flask(__name__)

# Guardar archivos pendientes por usuario
pending_users = {}

# ======================
# MASTERIZACIÓN
# ======================

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

# ======================
# BOT
# ======================

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "🔥 ARSENAL BÚNKER 🔥\n\n"
        "Envíame tu audio y lo dejo nivel estudio.\n"
        "💰 Costo: $49 MXN"
    )

@bot.message_handler(content_types=['audio', 'voice', 'document'])
def receive_audio(message):
    try:
        file_id = None

        if message.audio:
            file_id = message.audio.file_id
        elif message.voice:
            file_id = message.voice.file_id
        elif message.document:
            file_id = message.document.file_id

        if not file_id:
            bot.reply_to(message, "❌ Archivo no válido")
            return

        # Guardar archivo pendiente
        pending_users[message.chat.id] = file_id

        # Crear sesión Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'mxn',
                    'product_data': {
                        'name': 'Masterización Arsenal Búnker'
                    },
                    'unit_amount': 4900,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'https://t.me/{BOT_USERNAME}',
            cancel_url=f'https://t.me/{BOT_USERNAME}',
            metadata={'chat_id': message.chat.id}
        )

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💳 Pagar y desbloquear", url=session.url))

        bot.send_message(
            message.chat.id,
            "💰 Para procesar tu audio, realiza el pago:",
            reply_markup=markup
        )

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# ======================
# WEBHOOK STRIPE
# ======================

@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    try:
        event = stripe.Event.construct_from(request.json, stripe.api_key)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            chat_id = int(session['metadata']['chat_id'])

            file_id = pending_users.get(chat_id)

            if not file_id:
                return '', 200

            # Descargar archivo
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            temp_file = f"temp_{chat_id}"
            wav_input = f"input_{chat_id}.wav"
            output_file = f"output_{chat_id}.wav"

            with open(temp_file, 'wb') as f:
                f.write(downloaded_file)

            # Convertir a WAV
            audio = AudioSegment.from_file(temp_file)
            audio.export(wav_input, format="wav")

            # Procesar
            masterizar_audio(wav_input, output_file)

            # Enviar resultado
            with open(output_file, 'rb') as f:
                bot.send_audio(chat_id, f, caption="🔥 Masterización lista - Arsenal Búnker")

            # Limpieza
            os.remove(temp_file)
            os.remove(wav_input)
            os.remove(output_file)

            # Eliminar de pendientes
            del pending_users[chat_id]

    except Exception as e:
        print(f"Error webhook: {str(e)}")

    return '', 200

# ======================
# KEEP ALIVE
# ======================

@app.route('/')
def home():
    return "Arsenal Búnker activo"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# ======================
# MAIN
# ======================

if __name__ == "__main__":
    print("🚀 Arsenal Búnker iniciado")

    Thread(target=run_flask).start()
    bot.infinity_polling()
