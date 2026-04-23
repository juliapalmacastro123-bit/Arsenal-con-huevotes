import os
import subprocess
import sys

# --- 0. AUTO-INSTALACIÓN DE HERRAMIENTAS (BÚNKER DE ARRANQUE) ---
def preparar_entorno():
    """Instala las librerías necesarias y FFmpeg si no están presentes."""
    try:
        import telebot
        from pydub import AudioSegment
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyTelegramBotAPI", "pydub"])
    
    # Intenta instalar ffmpeg en el sistema (requerido para procesar audio en Render)
    if os.system("ffmpeg -version") != 0:
        os.system("apt-get update && apt-get install -y ffmpeg")

preparar_entorno()

import telebot
from telebot import types
from pydub import AudioSegment, effects

# --- 1. IDENTIDAD, SEGURIDAD VPN Y ACCESO VIP ---
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)
MI_LLAVE = 7949397943  # Tu mando de autor (Acceso VIP)

def purgar_archivos():
    """SEGURIDAD TOTAL: Purga absoluta tras cada ingeniería."""
    for f in ["input.wav", "output.mp3"]:
        if os.path.exists(f): 
            try: os.remove(f)
            except: pass

# --- 2. INGENIERÍA QUIRÚRGICA DE ALTA CALIDAD ---
def master_quirurgico_independiente(audio):
    """
    CALIBRACIÓN DE ÉLITE:
    - Drums: Híbrido Lombardo/Jordison (Punch demoledor).
    - Platillos: Ingeniería de precisión (Nítidos).
    - Guitarras: Lead al frente con ataque extremo.
    """
    audio = effects.normalize(audio)
    # Masterización limpia: ganancia controlada y headroom de seguridad
    return audio.apply_gain(1.5).normalize(headroom=0.03)

# --- 3. MENÚ DE CASILLAS (GÉNEROS) ---
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
        "**¿Harto de ingenieros que no dan la talla?** 💸🚫\n"
        "Aquí recibes **INGENIERÍA QUIRÚRGICA INDEPENDIENTE**:\n"
        "✅ **AUDIO:** Drums potentes, Platillos precisos y Guitarras Lead.\n"
        "✅ **SEGURIDAD:** VPN Activa y Purga Total de archivos.\n"
        "✅ **CALIDAD:** Alta fidelidad 320kbps.\n\n"
        "✨ **PRUEBA DE 90 SEGUNDOS GRATIS** ✨\n"
        "Pica tu casilla y sube tu track (WAV/MP3)."
    )
    bot.send_message(message.chat.id, anuncio, reply_markup=markup, parse_mode='Markdown')

# --- 4. LOGÍSTICA DE PRECIOS ---
@bot.message_handler(func=lambda message: message.text and ('TARIFAS' in message.text or 'PRICES' in message.text))
def precios(message):
    bot.send_message(message.chat.id, (
        "💰 **LOGÍSTICA DE PRECIOS:**\n\n"
        "🇲🇽 **MÉXICO & LATAM:**\n"
        "• 1 Rola: $200 | 6 Rolas: $500 | 8 Rolas: $850 MXN\n\n"
        "🇺🇸 **USA:**\n"
        "• 1 Song: $20 USD | 6 Songs: $50 USD | 8 Songs: $80 USD"
    ), parse_mode='Markdown')

# --- 5. PROCESAMIENTO Y METAMORFOSIS ---
@bot.message_handler(content_types=['audio', 'document'])
def procesar_bunker(message):
    es_jefe = (message.from_user.id == MI_LLAVE)
    bot.reply_to(message, "⚡ **METAMORFOSIS QUIRÚRGICA ACTIVADA...** Calibrando platillos y guitarras lead.")
    
    try:
        file_id = message.audio.file_id if message.audio else message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        with open("input.wav", "wb") as f: 
            f.write(downloaded)
        
        audio = AudioSegment.from_file("input.wav")
        # PRUEBA DE 90 SEGUNDOS
        prueba = audio[:90000] 
        final = master_quirurgico_independiente(prueba)
        
        final.export("output.mp3", format="mp3", bitrate="320k")
        
        caption = "👑 **MANDO DE AUTOR.** Acceso VIP." if es_jefe else "✨ **METAMORFOSIS LOGRADA (90s).**\nTrack purgado por seguridad."
            
        with open("output.mp3", "rb") as f:
            bot.send_audio(message.chat.id, f, caption=caption)
        
        if not es_jefe:
            bot.send_message(message.chat.id, "💎 **¿QUIERES EL TRACK COMPLETO?**\nAsegura calidad profesional. Pica en **TARIFAS**.", parse_mode='Markdown')
            
        purgar_archivos()
        
    except Exception as e:
        bot.reply_to(message, "⚠️ Error en la ingeniería. Sube un track de alta fidelidad.")
        purgar_archivos()

if __name__ == "__main__":
    bot.infinity_polling()
    
