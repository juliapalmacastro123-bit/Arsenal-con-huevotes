import os
import telebot
from telebot import types
from pydub import AudioSegment, effects

# --- 1. IDENTIDAD Y CONFIGURACIÓN ---
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)
MI_LLAVE = 7949397943 

def purgar_archivos():
    """Purga absoluta tras cada ingeniería."""
    for f in ["input.wav", "output.mp3"]:
        if os.path.exists(f): 
            try: os.remove(f)
            except: pass

# --- 2. INGENIERÍA QUIRÚRGICA ---
def master_quirurgico_independiente(audio):
    audio = effects.normalize(audio)
    return audio.apply_gain(1.5).normalize(headroom=0.03)

# --- 3. MENÚ DE CASILLAS ---
@bot.message_handler(commands=['start'])
def inicio(message):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.add(
        types.KeyboardButton('💀 THRASH METAL'), types.KeyboardButton('🩸 DEATH METAL'),
        types.KeyboardButton('🌑 BLACK METAL'), types.KeyboardButton('☣️ GRINDCORE'),
        types.KeyboardButton('👊 HARDCORE'), types.KeyboardButton('🎸 HEAVY METAL'),
        types.KeyboardButton('💄 GLAM METAL'), types.KeyboardButton('🔥 HARD ROCK'),
        types.KeyboardButton('🎤 ROCK URBANO'), types.KeyboardButton('🏁 SKA'),
        types.KeyboardButton('🤘 PUNK'), types.KeyboardButton('🎸 PUNK ROCK'),
        types.KeyboardButton('🎸 INDIE'), types.KeyboardButton('🌎 ROCK LATINO'),
        types.KeyboardButton('💰 TARIFAS / PRICES')
    )
    
    anuncio = (
        "🚀 **ARSENAL: SOUND METAMORPHOSIS**\n"
        "⚡ *La Metamorfosis del Sonido* ⚡\n\n"
        "Aquí recibes **INGENIERÍA QUIRÚRGICA INDEPENDIENTE**.\n"
        "✨ **PRUEBA DE 90 SEGUNDOS GRATIS** ✨"
    )
    bot.send_message(message.chat.id, anuncio, reply_markup=markup, parse_mode='Markdown')

# --- 4. PRECIOS ---
@bot.message_handler(func=lambda message: message.text and ('TARIFAS' in message.text or 'PRICES' in message.text))
def precios(message):
    bot.send_message(message.chat.id, (
        "💰 **LOGÍSTICA DE PRECIOS:**\n\n"
        "🇲🇽 **MX:** 1 Rola: $200 | 6: $500\n"
        "🇺🇸 **USA:** 1 Song: $20 | 6: $50"
    ), parse_mode='Markdown')

# --- 5. PROCESAMIENTO ---
@bot.message_handler(content_types=['audio', 'document'])
def procesar_bunker(message):
    es_jefe = (message.from_user.id == MI_LLAVE)
    bot.reply_to(message, "⚡ **METAMORFOSIS QUIRÚRGICA ACTIVADA...**")
    
    try:
        file_id = message.audio.file_id if message.audio else message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        with open("input.wav", "wb") as f: f.write(downloaded)
        
        audio = AudioSegment.from_file("input.wav")
        prueba = audio[:90000] 
        final = master_quirurgico_independiente(prueba)
        final.export("output.mp3", format="mp3", bitrate="320k")
        
        caption = "👑 **MANDO DE AUTOR.**" if es_jefe else "✨ **METAMORFOSIS LOGRADA.**"
        with open("output.mp3", "rb") as f:
            bot.send_audio(message.chat.id, f, caption=caption)
        purgar_archivos()
    except Exception as e:
        bot.reply_to(message, "⚠️ Error. Sube un track válido.")
        purgar_archivos()

if __name__ == "__main__":
    bot.infinity_polling()
    
