import os
import telebot
import time

# Tu token de BotFather
TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)

# --- ESTA LÍNEA ES LA QUE ARREGLA EL ERROR 409 ---
bot.remove_webhook()
time.sleep(1) 

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "¡Arsenal Total en línea! 🤘 ¿Qué vamos a armar hoy?")

if __name__ == "__main__":
    print("Bot arrancando...")
    bot.infinity_polling()
