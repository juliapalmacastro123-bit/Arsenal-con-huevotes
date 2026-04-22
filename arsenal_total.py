import telebot
from telebot import types

# --- TU TOKEN QUE YA TENÍAMOS DESDE HACE 3 DÍAS ---
TOKEN = '7982269986:AAF2_xY-6_z9_8_7_6_5_4_3_2_1_A_B_C' 

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def inicio(message):
    user_lang = message.from_user.language_code
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    
    if user_lang == 'es':
        msg = (
            "🚀 **BIENVENIDO AL ARSENAL BÚNKER**\n\n"
            "Erick, hoy es el día en que **dejaremos huella y saltaremos al éxito.**\n\n"
            "1️⃣ Sube tu audio (MP3/WAV)\n"
            "2️⃣ Recibe prueba de 90 segundos masterizada\n"
            "3️⃣ Paga y libera el Master completo"
        )
        markup.add(types.KeyboardButton('🎤 Mando de Autor'))
    else:
        msg = (
            "🚀 **WELCOME TO ARSENAL BUNKER**\n\n"
            "High-end engineering. Your music, our mark.\n\n"
            "1️⃣ Upload audio\n"
            "2️⃣ Get 90s preview\n"
            "3️⃣ Pay and unlock Full Master"
        )
        markup.add(types.KeyboardButton('🎤 Author Command'))

    bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode='Markdown')

# Aquí sigue tu ingeniería de FFmpeg que ya tienes blindada...

if __name__ == "__main__":
    print("El Arsenal-con-huevotes está patrullando...")
    bot.infinity_polling()
    
