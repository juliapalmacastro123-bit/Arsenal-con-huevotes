import os
import time
import telebot
from telebot import types
from flask import Flask, request
import subprocess
import shutil

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

BOT_NAME = "ARSENAL: The Sound Metamorphosis"

# ======================
# CHECK FFMPEG
# ======================

if not shutil.which("ffmpeg"):
    raise RuntimeError("FFmpeg no está instalado en el servidor")

# ======================
# ADMIN
# ======================

ADMIN_ID = 7949397943

def is_admin(uid):
    return uid == ADMIN_ID

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
# REGIONES
# ======================

regions = {}

def is_int(chat_id):
    return regions.get(chat_id) == "🌎 INTERNATIONAL"

# ======================
# LINK ÚNICO
# ======================

PAGO_LINK = "https://mpago.la/2KNKzJp"

# ======================
# PAGOS
# ======================

def pagos(chat_id):

    kb = types.InlineKeyboardMarkup()

    if is_int(chat_id):

        kb.add(types.InlineKeyboardButton("⚡
