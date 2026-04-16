"""
Radar Maestro - Bot de Cuotas Deportivas
Bot principal de Telegram con inteligencia artificial
"""

import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Variables globales
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start - Bienvenida"""
    user = update.effective_user
    await update.message.reply_text(
        f"¡Hola {user.first_name}! 👋\n\n"
        "Bienvenido a Radar Maestro\n"
        "Bot inteligente de análisis de cuotas deportivas\n\n"
        "Comandos disponibles:\n"
        "/picks - Ver picks del día\n"
        "/rendimiento - Tu rendimiento\n"
        "/valor - Alertas de valor\n"
        "/bank - Tu bankroll\n"
        "/ayuda - Más información"
    )


async def picks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /picks - Mostrar picks del día"""
    await update.message.reply_text(
        "📊 Picks del día:\n\n"
        "Cargando análisis inteligente..."
    )


async def rendimiento(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /rendimiento - Mostrar rendimiento"""
    await update.message.reply_text(
        "📈 Tu rendimiento:\n\n"
        "ROI: +15.5%\n"
        "Aciertos: 62%\n"
        "Yield: +2.3%"
    )


async def valor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /valor - Alertas de valor"""
    await update.message.reply_text(
        "💎 Alertas de valor encontradas:\n\n"
        "🔴 Fútbol - La Liga\n"
        "Real Madrid vs Barcelona\n"
        "Cuota: 1.95 | Valor: +3.2%"
    )


async def bank(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /bank - Mostrar bankroll"""
    await update.message.reply_text(
        "💰 Tu Bankroll:\n\n"
        "Saldo: $1,000.00\n"
        "Ganancia: +$150.00\n"
        "ROI: +15%"
    )


async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /ayuda - Mostrar ayuda"""
    await update.message.reply_text(
        "ℹ️ Ayuda - Radar Maestro\n\n"
        "Somos un bot especializado en análisis inteligente de cuotas\n"
        "Usamos algoritmos avanzados para detectar valor\n\n"
        "¿Qué es valor?\n"
        "Cuando la probabilidad real es mayor que la implícita en la cuota"
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")


def main() -> None:
    """Start the bot"""
    # Crear aplicación
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Agregar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("picks", picks))
    application.add_handler(CommandHandler("rendimiento", rendimiento))
    application.add_handler(CommandHandler("valor", valor))
    application.add_handler(CommandHandler("bank", bank))
    application.add_handler(CommandHandler("ayuda", ayuda))

    # Log all errors
    application.add_error_handler(error_handler)

    # Iniciar bot
    logger.info("🤖 Radar Maestro iniciando...")
    application.run_polling()


if __name__ == '__main__':
    main()
