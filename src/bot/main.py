"""
Bot principal de Telegram - Radar Maestro
"""

import logging
import os
import sys
from dotenv import load_dotenv
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

from handlers import BotHandlers, WAITING_BANKROLL

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
        logger.error("ERROR: TELEGRAM_TOKEN no configurado en .env")
        print("Configura TELEGRAM_TOKEN en tu archivo .env")
        return

    logger.info("Iniciando Radar Maestro Bot...")

    from src.models.database import init_db
    init_db()

    app = Application.builder().token(token).build()

    # ConversationHandler para /bank (configura bankroll)
    bank_conv = ConversationHandler(
        entry_points=[CommandHandler("bank", BotHandlers.cmd_bank)],
        states={
            WAITING_BANKROLL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND,
                               BotHandlers.recibir_bankroll)
            ],
        },
        fallbacks=[CommandHandler("start", BotHandlers.cmd_start)],
        per_message=False,
    )

    app.add_handler(bank_conv)

    # Comandos simples
    app.add_handler(CommandHandler("start", BotHandlers.cmd_start))
    app.add_handler(CommandHandler("valor", BotHandlers.cmd_valor))
    app.add_handler(CommandHandler("rendimiento", BotHandlers.cmd_rendimiento))

    # Callbacks de botones inline
    app.add_handler(CallbackQueryHandler(BotHandlers.button_callback))

    # Mensajes de texto libre (flujo de apuesta / cambio de bank)
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, BotHandlers.mensaje_texto
    ))

    logger.info("Bot iniciado correctamente")
    app.run_polling(
        allowed_updates=['message', 'callback_query'],
        drop_pending_updates=True
    )


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot detenido por el usuario")
    except Exception as e:
        logger.error("Error fatal: %s", e)
        raise

