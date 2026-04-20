import asyncio
import os
from telegram import Bot

TOKEN = os.getenv('TELEGRAM_TOKEN')
GRUPOS = [8372489384] 

mensaje = "🚀 **¡BÚNKER QUIRÚRGICO ACTIVO!**\n\nErick, el Arsenal por fin está disparando. ¡Misión cumplida!"

async def disparar_arsenal():
    bot = Bot(token=TOKEN)
    for grupo_id in GRUPOS:
        try:
            await bot.send_message(chat_id=grupo_id, text=mensaje, parse_mode='Markdown')
            print(f"✅ Enviado a {grupo_id}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(disparar_arsenal())
    
