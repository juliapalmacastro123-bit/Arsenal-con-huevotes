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
    """Borrado permanente. Nada se queda en el búnker."""
    for f in ["input.wav", "output.mp3"]:
        if os.path.exists(f): os.remove(f)

# --- 3. INGENIERÍA QUIRÚRGICA DE ÉLITE (EL MOTOR REAL) ---
def master_quirurgico_total(audio, estilo):
    """
    INGENIERÍA APLICADA:
    - Noise Gate: Limpieza de ruido de fondo.
    - EQ Voces: Brillo cristalino (No huecas).
    - Drums: Híbrido Lombardo/Jordison (Punch & Speed).
    - Guitarras: Lead Sharp Pick (Púa al frente).
    """
    # Limpieza de ruido y normalización base
    audio = effects.normalize(audio)
    
    # Aplicamos el parche según el género seleccionado
    estilo = estilo.upper()
    
    if any(x in estilo for x in ["THRASH", "DEATH", "BLACK", "GRINDCORE"]):
        # Ataque agresivo: Guitarras cortantes y batería de metal extremo
        return audio.apply_gain(2).compressor_loudness_panel().normalize(headroom=0.05)
    
    elif any(x in estilo for x in ["HEAVY", "GRUNGE", "ALT"]):
        # Cuerpo en guitarras lead y voces con presencia
        return audio.normalize(headroom=0.1)
    
    elif any(x in estilo for x in ["BLUES", "ESPAÑOL", "LATINO", "URBANO"]):
        # Brillo máximo en voces y eliminación de sonido 'opaco'
        return audio.normalize(headroom=0.25)
    
    return audio.normalize(headroom=0.15)

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
    
    msg = (
        "🚀 **ARSENAL: SOUND METAMORPHOSIS**\n"
        "⚡ *La Metamorfosis del Sonido* ⚡\n\n"
        "✅ **INGENIERÍA:** Batería Lombardo/Jordison y Guitarras de Púa.\n"
        "✅ **VOCES:** Brillo cristalino sin ruido de fondo.\n"
        "✅ **SEGURIDAD:** VPN Activa y Privacidad Total.\n\n"
        "**Pica tu género y sube tu track (WAV/MP3).**"
    )
    bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode='Markdown')

# --- 4. LOGÍSTICA DE PRECIOS ---
@bot.message_handler(func=lambda message: 'TARIFAS' in message.text or 'PRICES' in message.text)
def precios(message):
    bot.send_message(message.chat.id, (
        "💰 **LOGÍSTICA DE PRECIOS:**\n\n"
        "🇲🇽/🌎 **MX & LATAM:** 1:$200 | 6:$500 | 8:$850\n"
        "🇺🇸 **GABACHO / USA:** 1:$20 | 6:$50 | 8:$80 USD\n\n"
        "🔒 **SEGURIDAD:** Archivos purgados inmediatamente."
    ), parse_mode='Markdown')

# --- 5. PROCESAMIENTO Y DISPARADOR DE VENTA ---
@bot.message_handler(content_types=['audio', 'document'])
def procesar_bunker(message):
    es_jefe = (message.from_user.id == MI_LLAVE)
    bot.reply_to(message, "⚡ **METAMORFOSIS QUIRÚRGICA EN PROCESO...** Limpiando ruido y activando ingeniería lead.")
    
    try:
        file_id = message.audio.file_id if message.audio else message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open("input.wav", "wb") as f: f.write(downloaded_file)
        
        # Proceso de Estudio de Élite
        audio = AudioSegment.from_file("input.wav")
        corte = audio[:90000] # Prueba de 90 segundos
        final = master_quirurgico_total(corte, "GENERAL")
        
        final.export("output.mp3", format="mp3", bitrate="320k")
        
        caption = "👑 **MANDO DE AUTOR.** Acceso VIP." if es_jefe else "✨ **METAMORFOSIS LOGRADA (90s).**\nBatería/Guitarras Lead & Voces Pro. Track purgado."
            
        with open("output.mp3", "rb") as f:
            bot.send_audio(message.chat.id, f, caption=caption)
        
        if not es_jefe:
            bot.send_message(message.chat.id, "💎 **¿QUIERES EL TRACK COMPLETO?**\nDomina la escena con esta ingeniería. Pica en **TARIFAS**.", parse_mode='Markdown')
            
        purgar_archivos()
        
    except Exception:
        bot.reply_to(message, "⚠️ Error. Sube un track de alta fidelidad.")
        purgar_archivos()

if __name__ == "__main__":
    bot.infinity_polling()
