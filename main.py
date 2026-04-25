import os
import time
import telebot
from telebot import types
from flask import Flask, request
import subprocess

# ======================
# CONFIG
# ======================

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("Falta TOKEN")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
app = Flask(__name__)

BASE_URL = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_URL = f"{BASE_URL}/{TOKEN}" if BASE_URL else None

BOT_NAME = "ARSENAL: La Metamorfosis del Sonido"

PRIVACY = f"""
🔒 <b>{BOT_NAME}</b>

- No almacenamos audio
- Solo se procesa temporalmente
- Se elimina automáticamente
"""

ADMIN_ID = 7949397943
vip_users = set()

def is_vip(uid):
    return uid == ADMIN_ID or uid in vip_users

# ======================
# ANTI SPAM
# ======================

last_time = {}

def anti_spam(uid):
    now = time.time()
    if now - last_time.get(uid, 0) < 6:
        return False
    last_time[uid] = now
    return True

# ======================
# REGIONES / PAGOS
# ======================

regions = {}

LINKS = {
    "MX_1": "https://mpago.la/2dMaFNh",
    "MX_6": "https://mpago.la/REEMPLAZAR",
    "MX_8": "https://mpago.la/REEMPLAZAR",
    "US_1": "https://example.com",
    "US_6": "https://example.com",
    "US_8": "https://example.com"
}

def is_int(chat_id):
    return "INTERNACIONAL" in regions.get(chat_id, "")

def pagos(chat_id):
    try:
        kb = types.InlineKeyboardMarkup()

        if is_int(chat_id):
            kb.add(types.InlineKeyboardButton("🎧 1 Track - $20", url=LINKS["US_1"]))
            kb.add(types.InlineKeyboardButton("🔥 6 Tracks - $50", url=LINKS["US_6"]))
            kb.add(types.InlineKeyboardButton("💎 8 Tracks - $80", url=LINKS["US_8"]))
        else:
            kb.add(types.InlineKeyboardButton("🎧 1 Rola - $200", url=LINKS["MX_1"]))
            kb.add(types.InlineKeyboardButton("🔥 6 Rolas - $500", url=LINKS["MX_6"]))
            kb.add(types.InlineKeyboardButton("💎 8 Rolas - $850", url=LINKS["MX_8"]))

        bot.send_message(chat_id, "💳 <b>ARSENAL PRO</b>\nElige tu pack 🔥", reply_markup=kb)

    except Exception as e:
        print("ERROR PAGOS:", e)
        bot.send_message(chat_id, "💳 Sistema en mantenimiento")

# ======================
# LIMPIEZA
# ======================

def clean():
    for f in ["input.ogg", "temp.wav", "output.mp3"]:
        if os.path.exists(f):
            os.remove(f)

# ======================
# 🎛️ MASTER ENGINE FINAL (METAL / ROCK / PRO)
# ======================

def master(inp, out):
    subprocess.run([
        "ffmpeg", "-y",
        "-i", inp,

        "-af",
        (

            # ======================
            # LIM
