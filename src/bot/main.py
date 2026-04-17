"""
Bot principal de Telegram - Radar Maestro
"""

import logging
import os
import sys
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

# Cargar variables de entorno
load_dotenv()

# Importar handlers
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.bot.handlers import BotHandlers
from src.models.database import init_db

# Configurar logging
os.makedirs('logs', exist_ok=True)
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

    token = os.getenv('TELEGRAM_TOKEN')

    if not token:
        logger.error("❌ ERROR: TELEGRAM_TOKEN no configurado en .env")
        print("⚠️ Por favor configura TELEGRAM_TOKEN en tu archivo .env")
        return

    logger.info(f"✅ Token: {token[:20]}...")

    # Inicializar base de datos
    init_db()

    logger.info("✅ Bot ready")

    # Crear aplicación con job queue habilitado
    app = Application.builder().token(token).build()

    # ---- Comandos ----
    app.add_handler(CommandHandler("start", BotHandlers.cmd_start))
    app.add_handler(CommandHandler("picks", BotHandlers.cmd_picks))
    app.add_handler(CommandHandler("valor", BotHandlers.cmd_valor))
    app.add_handler(CommandHandler("bank", BotHandlers.cmd_bank))
    app.add_handler(CommandHandler("historial", BotHandlers.cmd_historial))
    app.add_handler(CommandHandler("combinada", BotHandlers.cmd_ver_combinada))
    app.add_handler(CommandHandler("ayuda", BotHandlers.cmd_ayuda))

    # ---- Callbacks de botones inline ----
    app.add_handler(CallbackQueryHandler(BotHandlers.button_callback))

    # ---- Job queue: alerta 30 min antes de partidos con valor ----
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(
            BotHandlers.job_alertas_30min,
            interval=60,   # cada 60 segundos
            first=10,
            name='alertas_30min',
        )
        logger.info("✅ Job de alertas 30min registrado")

    logger.info("⏳ Polling...")

    app.run_polling(
        allowed_updates=['message', 'callback_query'],
        drop_pending_updates=True,
    )


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("⏹️ Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        raise

