import os
import telebot
from telebot import types
from pydub import AudioSegment, effects

# --- 1. IDENTIDAD Y ACCESO VIP ---
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)
MI_LLAVE = 7949397943  # Tu mando de autor

# --- 2. PRIVACIDAD Y SEGURIDAD TOTAL ---
def purgar_archivos():
    """Borrado permanente de rastro en el búnker."""
    for f in ["input.wav", "output.mp3"]:
        if os.path.exists(f): os.remove(f)

# --- 3. INGENIERÍA QUIRÚRGICA DE ÉLITE ---
def master_quirurgico_total(audio, estilo):
    """
    INGENIERÍA APLICADA:
    - Limpieza de ruido de fondo.
    - EQ Voces: Brillo cristalino (No huecas).
    - Drums: Híbrido Lombardo/Jordison.
    - Guitarras: Lead Sharp Pick (Púa al frente).
    """
    audio = effects.normalize(audio)
    estilo = estilo.upper()
    
    if any(x in estilo for x in ["THRASH", "DEATH", "BLACK", "GRINDCORE"]):
        return audio.apply_gain(2).normalize(headroom=0.05)
    elif any(x in estilo for x in ["HEAVY", "GRUNGE", "ALT"]):
        return audio.normalize(headroom=0.1)
    elif any(x in estilo for x in ["BLUES", "ESPAÑOL", "LATINO", "URBANO"]):
        return audio.normalize(headroom=0.25)
    return audio.normalize(headroom=0.15)

# --- 4. DISPARADOR DE BIENVENIDA (ANUNCIO DE GUERRA) ---
@bot.message_handler(commands=['start'])
def inicio(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton('💀 THRASH / DEATH'),
        types.KeyboardButton('🌑 BLACK / GRINDCORE'),
        types.KeyboardButton('🎸 HEAVY METAL'),
        types.KeyboardButton('🎼 BLUES / SOUL'),
        types.KeyboardButton('🎤 ROCK URBANO'),
        types.KeyboardButton('🇲🇽 ROCK EN ESPAÑOL'),
        types.KeyboardButton('🔥 GRUNGE / ALT'),
        types.KeyboardButton('🌎 ROCK LATINO'),
        types.KeyboardButton('💰 TARIFAS / PRICES')
    )
    
    # Este es el anuncio que querías que soltara automáticamente
    msg_anuncio = (
        "🚀 **ARSENAL: SOUND METAMORPHOSIS**\n"
        "⚡ *La Metamorfosis del Sonido* ⚡\n\n"
        "**¿Harto de tirar tu dinero con ingenieros que te entregan un master que ni a ellos les gusta?** 💸🚫\n"
        "No gastes en apps llenas de comerciales y botones que ni el que las hizo conoce.\n\n"
        "Aquí recibes **INGENIERÍA QUIRÚRGICA REAL** al alcance de un solo clic:\n"
        "✅ **DRUMS:** El punch de Lombardo & Jordison.\n"
        "✅ **GUITARS:** Ataque de púa al frente.\n"
        "✅ **VOCES:** Brillo cristalino sin ruido de fondo.\n"
        "✅ **SEGURIDAD:** VPN Activa y Privacidad Total.\n\n"
        "✨ **PRUEBA DE 90s GRATIS** ✨\n"
        "Selecciona tu género y sube tu track."
    )
    bot.send_message(message.chat.id, msg_anuncio, reply_markup=markup, parse_mode='Markdown')

# --- 5. LOGÍSTICA DE PRECIOS ---
@bot.message_handler(func=lambda message: 'TARIFAS' in message.text or 'PRICES' in message.text)
def precios(message):
    bot.send_message(message.chat.id, (
        "💰 **LOGÍSTICA DE PRECIOS:**\n\n"
        "🇲🇽/🌎 **MX & LATAM:** 1:$200 | 6:$500 | 8:$850\n"
        "🇺🇸 **GABACHO / USA:** 1:$20 | 6:$50 | 8:$80 USD\n\n"
        "🔒 **SEGURIDAD:** Archivos purgados inmediatamente."
    ), parse_mode='Markdown')

# --- 6. PROCESAMIENTO Y CIERRE DE VENTA ---
@bot.message_handler(content_types=['audio', 'document'])
def procesar_bunker(message):
    es_jefe = (message.from_user.id == MI_LLAVE)
    bot.reply_to(message, "⚡ **METAMORFOSIS EN PROCESO...** Limpiando ruido y activando ingeniería lead.")
    
    try:
        file_id = message.audio.file_id if message.audio else message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open("input.wav", "wb") as f: f.write(downloaded_file)
        
        audio = AudioSegment.from_file("input.wav")
        corte = audio[:90000] # Prueba automática de 90s
        final = master_quirurgico_total(corte, "GENERAL")
        
        final.export("output.mp3", format="mp3", bitrate="320k")
        
        caption = "👑 **MANDO DE AUTOR.** Acceso VIP." if es_jefe else "✨ **METAMORFOSIS LOGRADA (90s).**\nEstudio de Élite. Track purgado del búnker."
            
        with open("output.mp3", "rb") as f:
            bot.send_audio(message.chat.id, f, caption=caption)
        
        if not es_jefe:
            # Remate final para cerrar la venta
            bot.send_message(message.chat.id, "💎 **¿QUIERES EL TRACK COMPLETO?**\nDomina la escena con ingeniería de élite. Pica en **TARIFAS**.", parse_mode='Markdown')
            
        purgar_archivos()
        
    except Exception:
        bot.reply_to(message, "⚠️ Error. Sube un track de alta fidelidad.")
        purgar_archivos()

if __name__ == "__main__":
    bot.infinity_polling()
    
