import asyncio
import os
from telegram import Bot

# CONFIGURACIÓN QUIRÚRGICA
TOKEN = os.getenv('TELEGRAM_TOKEN')
# Aquí usamos el ID que ya tenemos verificado
GRUPOS = [8372489384] 

mensaje_arsenal = """
🔥 **ARSENAL QUIRÚRGICO ACTIVO** 🔥

✅ **Servicio:** Configuración de Búnker Bot
✅ **Estado:** Operativo 100%
✅ **Precisión:** Alta

¡El sistema está disparando correctamente! 🚀
"""

async def disparar_arsenal():
    bot = Bot(token=TOKEN)
    print("PANTALLA LCD: [INICIANDO SECUENCIA DE DISPARO]")
    for grupo_id in GRUPOS:
        try:
            await bot.send_message(chat_id=grupo_id, text=mensaje_arsenal, parse_mode='Markdown')
            print(f"PANTALLA LCD: [MENSAJE ENVIADO A {grupo_id}]")
        except Exception as e:
            print(f"PANTALLA LCD: [ERROR EN ID {grupo_id}]: {e}")

if __name__ == "__main__":
    asyncio.run(disparar_arsenal())
    
