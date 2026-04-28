import os
import threading
import logging
import stripe
from flask import Flask, request
import telebot
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range

TOKEN = os.getenv("TOKEN")
STRIPE_SECRET = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK = os.getenv("STRIPE_WEBHOOK_SECRET")

stripe.api_key = STRIPE_SECRET

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessions = {}

# ======================
# AUDIO ENGINE
# ======================

def metal_master(audio):
    audio = normalize(audio)
    audio = compress_dynamic_range(audio, threshold=-18, ratio=4)
    audio = audio.high_pass_filter(50)
    audio = audio.low_pass_filter(15500)
    audio = audio + 4
    return audio

def mix_metal(tracks):
    drums = normalize(tracks["drums"])
    bass = normalize(tracks["bass"])
    guitar = normalize(tracks["guitar"])
    vocals = normalize(tracks["vocals"])

    guitar = guitar.high_pass_filter(120) + 5
    guitar = guitar.pan(-0.3).overlay(guitar.pan(0.3))

    bass = bass.low_pass_filter(250)

    vocals = vocals.high_pass_filter(100) + 3

    mix = drums.overlay(bass)
    mix = mix.overlay(guitar)
    mix = mix.overlay(vocals)

    return metal_master(mix)

def preview(audio):
    p = audio[:90 * 1000]
    path = "/tmp/out.mp3"
    p.export(path, format="mp3")
    return path

# ======================
# STRIPE
# ======================

def pay(uid, amount, name, currency):
    s = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line
