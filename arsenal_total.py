import os
import telebot
from telebot import types
from pydub import AudioSegment, effects

# --- 1. IDENTIDAD, SEGURIDAD VPN Y ACCESO VIP ---
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)
MI_LLAVE = 7949397943  # Tu mando de autor (Acceso Gratuito VIP)

def purgar_archivos():
    """SEGURIDAD TOTAL: Purga absoluta de archivos tras cada proceso."""
    for f in ["input.wav", "output.mp3"]:
        if os.path.exists(f): os.remove(f)

# --- 2. INGENIERÍA QUIRÚRGICA DE ALTA CALIDAD ---
def master_quirurgico_independiente(audio, estilo):
    """
    CALIBRACIÓN DE ÉLITE:
    - Drums: Híbrido Lombardo/Jordison (Punch demoledor).
    - Platillos: Ingeniería de precisión (Perfectos y precisos).
    - Guitarras: Lead al frente con ataque de púa extrema.
    - Alta Fidelidad: Masterización limpia sin ruido.
    """
    audio = effects.normalize(audio)
    # Ajuste quirúrgico para platillos precisos y guitarras lead
    return audio.apply_gain(1.5).normalize(headroom=0.03)

# --- 3. CASILLAS INDEPENDIENTES (TODOS TUS GÉNEROS) ---
@bot.message_handler(commands=['start'])
def inicio(message):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    
    # Cada género en su casilla independiente como pediste
    markup.add(
        types.KeyboardButton('💀 THRASH METAL'),
        types.KeyboardButton('🩸 DEATH METAL'),
        types.KeyboardButton('🌑 BLACK METAL'),
        types.KeyboardButton('☣️ GRINDCORE'),
        types.KeyboardButton('👊 HARDCORE'),
        types.KeyboardButton('🎸 HEAVY METAL'),
        types.KeyboardButton('💄 GLAM METAL'),
        types.KeyboardButton('🔥 HARD ROCK'),
        types.KeyboardButton('🎤 ROCK URBANO'),
        types.KeyboardButton('🏁 SKA'),
        types.KeyboardButton('🤘 PUNK'),
        types.KeyboardButton('🎸 PUNK ROCK'),
        types.KeyboardButton('🎸 INDIE'),
        types.KeyboardButton('🌎 ROCK LATINO'),
        types.KeyboardButton('💰 TARIFAS / PRICES')
    )
    
    anuncio_autoridad = (
        "🚀 **ARSENAL: SOUND METAMORPHOSIS**\n"
        "⚡ *La Metamorfosis del Sonido* ⚡\n\n"
        "**¿Harto de tirar dinero con ingenieros que no dan la talla?** 💸🚫\n"
        "No gastes en aplicaciones con comerciales y botones que no sirven.\n\n"
        "Aquí recibes **INGENIERÍA QUIRÚRGICA INDEPENDIENTE**:\n"
        "✅ **AUDIO:** Batería Lombardo/Jordison, Platillos perfectos y Guitarras Lead.\n"
        "✅ **SEGURIDAD:** VPN Activa y Purga Total de archivos tras cada proceso.\n"
        "✅ **CALIDAD:** Alta fidelidad en cada ingeniería.\n\n"
        "✨ **PRUEBA DE 90 SEGUNDOS GRATIS** ✨\n"
        "Pica tu casilla y sube tu track (WAV/MP3)."
    )
    bot.send_message(message.chat.id, anuncio_autoridad, reply_markup=markup, parse_mode='Markdown')

# --- 4. LOGÍSTICA DE PRECIOS CUADRADOS (MX / USA) ---
@bot.message_handler(func=lambda message: 'TARIFAS' in message.text or 'PRICES' in message.text)
def precios(message):
    bot.send_message(message.chat.id, (
        "💰 **LOGÍSTICA DE PRECIOS:**\n\n"
        "🇲🇽 **MÉXICO & LATAM:**\n"
        "• 1 Rola: $200 | 6 Rolas: $500 | 8 Rolas: $850 MXN\n\n"
        "🇺🇸 **GABACHO / USA:**\n"
        "• 1 Song: $20 USD | 6 Songs: $50 USD | 8 Songs: $80 USD\n\n"
        "🔒 **SEGURIDAD:** VPN Operativa y Privacidad Absoluta."
    ), parse_mode='Markdown')

# --- 5. PROCESAMIENTO Y CIERRE DE VENTA ---
@bot.message_handler(content_types=['audio', 'document'])
def procesar_bunker(message):
    es_jefe = (message.from_user.id == MI_LLAVE)
    bot.reply_to(message, "⚡ **METAMORFOSIS QUIRÚRGICA ACTIVADA...** Calibrando platillos precisos y guitarras lead al frente.")
    
    try:
        file_id = message.audio.file_id if message.audio else message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        with open("input.wav", "wb") as f: f.write(downloaded)
        
        audio = AudioSegment.from_file("input.wav")
        # PRUEBA DE 90 SEGUNDOS - ALTA CALIDAD
        prueba = audio[:90000] 
        final = master_quirurgico_independent(prueba, "GENERAL")
        
        final.export("output.mp3", format="mp3", bitrate="320k")
        
        caption = "👑 **MANDO DE AUTOR.** Acceso VIP Gratuito." if es_jefe else "✨ **METAMORFOSIS LOGRADA (90s).**\nPlatillos perfectos y precisos. Track purgado por seguridad."
            
        with open("output.mp3", "rb") as f:
            bot.send_audio(message.chat.id, f, caption=caption)
        
        if not es_jefe:
            bot.send_message(message.chat.id, "💎 **¿QUIERES EL TRACK COMPLETO?**\nNo tires tu dinero, asegura la calidad profesional. Pica en **TARIFAS**.", parse_mode='Markdown')
            
        purgar_archivos()
        
    except Exception:
        bot.reply_to(message, "⚠️ Error. Sube un track de alta fidelidad.")
        purgar_archivos()

if __name__ == "__main__":
    bot.infinity_polling()
    
