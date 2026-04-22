import telebot
from telebot import types

# 1. PEGA TU TOKEN AQUÍ (El que te dio BotFather)
TOKEN = 'TU_TOKEN_AQUI'

bot = telebot.TeleBot(TOKEN)

# Comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    itembtn1 = types.KeyboardButton('🎸 Metal')
    itembtn2 = types.KeyboardButton('🎷 Ska')
    itembtn3 = types.KeyboardButton('🎺 Blues')
    itembtn4 = types.KeyboardButton('🛠️ Ingeniería Audio')
    
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
    
    bot.reply_to(message, "¡Bienvenido al Búnker, Erick!\n\nEl Arsenal está listo. Elige tu estilo o manda un audio para procesar:", reply_markup=markup)

# Manejo de mensajes de texto (Botones)
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text == '🎸 Metal':
        bot.reply_to(message, "🔥 Activando ecualización de Metal: Agudos crujientes y bajos potentes.")
    elif message.text == '🎷 Ska':
        bot.reply_to(message, "🏁 Modo Ska: Resaltando metales y ritmo constante.")
    elif message.text == '🎺 Blues':
        bot.reply_to(message, "🥃 Esencia Blues: Calidez sonora y medios definidos.")
    elif message.text == '🛠️ Ingeniería Audio':
        bot.reply_to(message, "🎧 Mando de Autor: Procesando señales con precisión.")
    else:
        bot.reply_to(message, "El Arsenal recibió tu mensaje. Usa el menú para configurar el sonido.")

# ESTA LÍNEA ES LA MÁS IMPORTANTE (Para que el bot no se apague)
if __name__ == "__main__":
    print("El Arsenal-con-huevotes está patrullando...")
    bot.infinity_polling()
