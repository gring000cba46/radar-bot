"""
Bot principal de Telegram - Radar Maestro
"""

import logging
import os
import sys
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Cargar variables de entorno
load_dotenv()

# Importar handlers
sys.path.insert(0, os.path.dirname(__file__))
from handlers import BotHandlers

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Punto de entrada del bot"""
    
    # Obtener token
    token = os.getenv('TELEGRAM_TOKEN')
    
    if not token:
        logger.error("❌ ERROR: TELEGRAM_TOKEN no configurado en .env")
        print("⚠️ Por favor configura TELEGRAM_TOKEN en tu archivo .env")
        return
    
    logger.info("🚀 Iniciando Radar Maestro Bot...")
    
    # Crear aplicación
    app = Application.builder().token(token).build()
    
    # Registrar handlers de comandos
    app.add_handler(CommandHandler("start", BotHandlers.cmd_start))
    app.add_handler(CommandHandler("picks", BotHandlers.cmd_picks))
    app.add_handler(CommandHandler("valor", BotHandlers.cmd_valor))
    app.add_handler(CommandHandler("rendimiento", BotHandlers.cmd_rendimiento))
    app.add_handler(CommandHandler("bank", BotHandlers.cmd_bank))
    app.add_handler(CommandHandler("ayuda", BotHandlers.cmd_ayuda))
    
    # Registrar handler de callbacks
    app.add_handler(CallbackQueryHandler(BotHandlers.button_callback))
    
    # Iniciar bot
    logger.info("✅ Bot iniciado correctamente")
    logger.info("⏳ Esperando mensajes...")
    
    app.run_polling(
        allowed_updates=['message', 'callback_query'],
        drop_pending_updates=True
    )


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("⏹️ Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        raise

