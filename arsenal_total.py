import os
import telebot
from telebot import types

# --- INGENIERÍA DE GRADO MILITAR ---
# Jalamos el TOKEN de la variable 'TOKEN' que ya configuraste en Render
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("❌ ERROR: No se encontró la variable TOKEN en Render.")
    bot = None
else:
    bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def inicio(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    msg = (
        "🚀 **BIENVENIDO AL ARSENAL BÚNKER**\n\n"
        "Erick, hoy es el día en que **dejaremos huella y saltaremos al éxito.**\n\n"
        "1️⃣ Sube tu audio (MP3/WAV)\n"
        "2️⃣ Recibe prueba de 90 segundos masterizada\n"
        "3️⃣ Paga y libera el Master completo"
    )
    markup.add(types.KeyboardButton('🎤 Mando de Autor'))
    bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def eco(message):
    bot.reply_to(message, "⚡ **Arsenal Operativo.** El búnker está bajo control, carnal.")

if __name__ == "__main__":
    if bot:
        print("🔥 El Arsenal-con-huevotes (arsenal_total.py) está patrullando...")
        bot.infinity_polling()
        
