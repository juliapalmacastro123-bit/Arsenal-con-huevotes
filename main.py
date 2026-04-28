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

if not TOKEN:
    raise ValueError("Falta TOKEN")

stripe.api_key = STRIPE_SECRET

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessions = {}

# ======================
# AUDIO ENGINE (METAL)
# ======================

def metal_master(audio):
    audio = normalize(audio)

    # compresión agresiva metal
    audio = compress_dynamic_range(
        audio,
        threshold=-18,
        ratio=5,
        attack=3,
        release=40
    )

    # limpieza
    audio = audio.high_pass_filter(50)
    audio = audio.low_pass_filter(15500)

    # presencia general
    audio = audio + 4

    # brillo controlado (voz + guitarras)
    bright = audio.high_pass_filter(4000) + 2
    audio = audio.overlay(bright)

    # “kick feel” (simulación)
    low = audio.low_pass_filter(120) + 2
    audio = audio.overlay(low)

    # pseudo stereo
    left = audio.pan(-0.25)
    right = audio.pan(0.25)
    audio = left.overlay(right)

    return audio

def mix_metal(tracks):
    drums = normalize(tracks["drums"])
    bass = normalize(tracks["bass"])
    guitar = normalize(tracks["guitar"])
    vocals = normalize(tracks["vocals"])

    # GUITARRAS AL FRENTE
    guitar = guitar.high_pass_filter(120) + 6
    guitar = guitar.pan(-0.4).overlay(guitar.pan(0.4))

    # BAJO
    bass = bass.low_pass_filter(250) + 2

    # VOZ
    vocals = vocals.high_pass_filter(100) + 3

    # DRUMS (pegada)
    drums = compress_dynamic_range(drums, threshold=-18, ratio=4)

    mix = drums.overlay(bass)
    mix = mix.overlay(guitar)
    mix = mix.overlay(vocals)

    return metal_master(mix)

def create_preview(audio):
    preview = audio[:90 * 1000]
    path = "/tmp/preview.mp3"
    preview.export(path, format="mp3")
    return path

# ======================
# STRIPE
# ======================

def pay(uid, amount, name, currency):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": currency,
                "product_data": {
                    "name": name
                },
                "unit_amount": int(amount * 100)
            },
            "quantity": 1
        }],
        mode="payment",
        client_reference_id=str(uid),
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel"
    )
    return session.url

# ======================
# BOT
# ======================

@bot.message_handler(commands=['start'])
def start(m):
    sessions[m.from_user.id] = {"mode": None, "tracks": {}, "step": None}
    bot.send_message(m.chat.id,
    "🤘 ARSENAL METAL SYSTEM\n\n1 = DEMO\n2 = PRO MULTITRACK")

@bot.message_handler(func=lambda m: m.text in ["1","2"])
def mode(m):
    uid = m.from_user.id

    if m.text == "1":
        sessions[uid]["mode"] = "demo"
        bot.send_message(m.chat.id, "🎧 Envía tu audio")

    else:
        sessions[uid]["mode"] = "pro"
        sessions[uid]["step"] = "drums"
        bot.send_message(m.chat.id, "🥁 Envía DRUMS")

@bot.message_handler(content_types=['audio','voice','document'])
def audio_handler(m):
    try:
        uid = m.from_user.id
        s = sessions.get(uid)

        if not s:
            bot.send_message(m.chat.id, "Usa /start")
            return

        file_id = m.audio.file_id if m.audio else \
                  m.voice.file_id if m.voice else \
                  m.document.file_id

        file_info = bot.get_file(file_id)
        data = bot.download_file(file_info.file_path)

        path = f"/tmp/{uid}_{len(os.listdir('/tmp'))}.wav"
        with open(path, "wb") as f:
            f.write(data)

        audio = AudioSegment.from_file(path)

        # ======================
        # DEMO
        # ======================

        if s["mode"] == "demo":
            mastered = metal_master(audio)
            preview = create_preview(mastered)

            with open(preview, "rb") as f:
                bot.send_audio(m.chat.id, f, "🤘 PREVIEW")

            bot.send_message(m.chat.id,
            "💳 DEMO\nMX: $200\nUS: $20")

        #
