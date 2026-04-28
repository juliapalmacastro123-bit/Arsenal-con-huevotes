import os
import threading
import logging
import stripe
from flask import Flask, request
import telebot
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range

# ======================
# CONFIG
# ======================

TOKEN = os.getenv("TOKEN")
STRIPE_SECRET = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK = os.getenv("STRIPE_WEBHOOK_SECRET")

stripe.api_key = STRIPE_SECRET

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

user_region = {}

# ======================
# AUDIO ENGINE (METAL)
# ======================

def metal_master(audio):
    audio = normalize(audio)
    audio = compress_dynamic_range(audio)

    # perfil metal (equilibrado)
    audio = audio.high_pass_filter(40)
    audio = audio.low_pass_filter(16000)

    # más presencia
    audio = audio + 3

    return audio

def create_preview(audio):
    preview = audio[:90 * 1000]
    path = "/tmp/final.mp3"
    preview.export(path, format="mp3")
    return path

# ======================
# STRIPE
# ======================

def create_payment(user_id, amount, name, currency):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": currency,
                "product_data": {"name": name},
                "unit_amount": int(amount * 100)
            },
            "quantity": 1
        }],
        mode="payment",
        client_reference_id=str(user_id),
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel"
    )
    return session.url

# ======================
# BOT
# ======================

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "🎧 ARSENAL METAL SYSTEM\nSelecciona región: MX o US")

@bot.message_handler(func=lambda m: m.text in ["MX", "US"])
def region(msg):
    user_region[msg.from_user.id] = msg.text
    bot.send_message(msg.chat.id, "⚡ Envía tu audio (preview 90s)")

@bot.message_handler(content_types=['audio', 'voice', 'document'])
def audio(msg):
    try:
        uid = msg.from_user.id
        region = user_region.get(uid, "MX")

        file_id = None
        if msg.audio:
            file_id = msg.audio.file_id
        elif msg.voice:
            file_id = msg.voice.file_id
        elif msg.document:
            file_id = msg.document.file_id

        file_info = bot.get_file(file_id)
        data = bot.download_file(file_info.file_path)

        path = "/tmp/input"
        with open(path, "wb") as f:
            f.write(data)

        audio = AudioSegment.from_file(path)
        mastered = metal_master(audio)

        preview_path = create_preview(mastered)

        with open(preview_path, "rb") as f:
            bot.send_audio(msg.chat.id, f, caption="🤘 METAL PREVIEW 90s")

        # ======================
        # PRECIOS CLAROS
        # ======================

        if region == "MX":
            text = """💳 PRECIOS MÉXICO

🎧 ESTÁNDAR
1 rola: $200
6 rolas: $500
8 rolas: $850

🔥 PRO
1 rola: $450
6 rolas: $1200
8 rolas: $1600
"""
        else:
            text = """💳 PRECIOS INTERNACIONALES

🎧 ESTÁNDAR
1 canción: $20
6 canciones: $50
8 canciones: $80

🔥 PREMIUM
1 canción: $50
6 canciones: $80
8 canciones: $120
"""

        bot.send_message(msg.chat.id, text)

        # ======================
        # LINKS DE PAGO
        # ======================

        bot.send_message(msg.chat.id, "💳 PAGAR:")

        if region == "MX":
            bot.send_message(msg.chat.id, f"1 rola → {create_payment(uid,200,'1 rola','mxn')}")
            bot.send_message(msg.chat.id, f"6 rolas → {create_payment(uid,500,'6 rolas','mxn')}")
            bot.send_message(msg.chat.id, f"8 rolas → {create_payment(uid,850,'8 rolas','mxn')}")
            bot.send_message(msg.chat.id, f"PRO 1 → {create_payment(uid,450,'pro 1','mxn')}")
            bot.send_message(msg.chat.id, f"PRO 6 → {create_payment(uid,1200,'pro 6','mxn')}")
            bot.send_message(msg.chat.id, f"PRO 8 → {create_payment(uid,1600,'pro 8','mxn')}")

        else:
            bot.send_message(msg.chat.id, f"1 canción → {create_payment(uid,20,'1 song','usd')}")
            bot.send_message(msg.chat.id, f"6 canciones → {create_payment(uid,50,'6 song','usd')}")
            bot.send_message(msg.chat.id, f"8 canciones → {create_payment(uid,80,'8 song','usd')}")
            bot.send_message(msg.chat.id, f"PRO 1 → {create_payment(uid,50,'pro 1','usd')}")
            bot.send_message(msg.chat.id, f"PRO 6 → {create_payment(uid,80,'pro 6','usd')}")
            bot.send_message(msg.chat.id, f"PRO 8 → {create_payment(uid,120,'pro 8','usd')}")

    except Exception as e:
        logging.error(e)
        bot.send_message(msg.chat.id, "❌ Error procesando audio")

# ======================
# WEBHOOK
# ======================

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.data
    sig = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK)
    except:
        return "error", 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print("PAGO OK:", session.get("client_reference_id"))

    return "ok", 200

# ======================
# RUN
# ======================

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    t = threading.Thread(target=run_bot)
    t.start()

    app.run(host="0.0.0.0", port=10000)
