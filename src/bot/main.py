"""
Radar Maestro - Bot de Cuotas Deportivas
Bot principal de Telegram con inteligencia artificial
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Importar handlers personalizados
from handlers import BotHandlers

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constantes
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN no configurado en .env")


class RadarBot:
    """Clase principal del bot de Telegram"""
    
    def __init__(self):
        self.token = TELEGRAM_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.application = None
        logger.info("🤖 Bot Radar Maestro inicializado")
    
    def build_application(self):
        """Construye la aplicación de telegram.ext"""
        self.application = Application.builder().token(self.token).build()
        
        # Registrar handlers de comandos
        self.application.add_handler(CommandHandler("start", BotHandlers.cmd_start))
        self.application.add_handler(CommandHandler("picks", BotHandlers.cmd_picks))
        self.application.add_handler(CommandHandler("rendimiento", BotHandlers.cmd_rendimiento))
        self.application.add_handler(CommandHandler("valor", BotHandlers.cmd_valor))
        self.application.add_handler(CommandHandler("bank", BotHandlers.cmd_bank))
        self.application.add_handler(CommandHandler("ayuda", BotHandlers.cmd_ayuda))
        
        # Registrar handler de callbacks
        self.application.add_handler(CallbackQueryHandler(BotHandlers.button_callback))
        
        # Registrar handler de mensajes de texto
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        logger.info("✅ Handlers registrados exitosamente")
        return self.application
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Maneja mensajes de texto generales"""
        user_message = update.message.text.lower()
        
        # Respuestas predefinidas
        respuestas = {
            'hola': '👋 ¡Hola! Usa /ayuda para ver todos los comandos disponibles',
            'ayuda': 'Usa /ayuda para obtener información completa del bot',
            'picks': 'Usa /picks para ver los picks del día',
            'valor': 'Usa /valor para ver solo oportunidades con valor real',
            'rendimiento': 'Usa /rendimiento para ver tu historial',
            'bank': 'Usa /bank para gestionar tu bankroll'
        }
        
        # Buscar coincidencias
        for palabra_clave, respuesta in respuestas.items():
            if palabra_clave in user_message:
                await update.message.reply_text(respuesta)
                return
        
        # Respuesta por defecto
        await update.message.reply_text(
            "🤔 No entiendo ese comando. Usa /ayuda para ver qué puedo hacer"
        )
    
    async def enviar_alerta_pick(self, chat_id: int, pick: dict) -> None:
        """Envía alerta de un nuevo pick"""
        mensaje = (
            f"🎯 **NUEVO PICK DETECTADO**\n\n"
            f"📊 {pick['partido']}\n"
            f"💰 Mercado: {pick['mercado']}\n"
            f"Cuota: {pick['cuota']}\n"
            f"Valor: {pick['valor']}\n"
            f"EV: {pick['ev']}\n"
            f"Confianza: {pick['confianza']}"
        )
        
        try:
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=mensaje,
                parse_mode='Markdown'
            )
            logger.info(f"✅ Alerta enviada a {chat_id}")
        except Exception as e:
            logger.error(f"❌ Error enviando alerta: {e}")
    
    async def enviar_reporte_diario(self, chat_id: int) -> None:
        """Envía reporte diario de rendimiento"""
        mensaje = (
            "📈 **REPORTE DIARIO**\n"
            f"Fecha: {datetime.now().strftime('%d/%m/%Y')}\n\n"
            
            "**PICKS**\n"
            "Generados: 12\n"
            "Con valor: 8\n"
            "Apostados: 6\n\n"
            
            "**RESULTADOS**\n"
            "Apuestas: 24\n"
            "Aciertos: 15 ✅\n"
            "Fallos: 9 ❌\n"
            "Tasa: 62.5%\n\n"
            
            "**BANKROLL**\n"
            "Saldo: $1,150.50\n"
            "Ganancia: +$150.50\n"
            "ROI: +15.05%\n\n"
            
            "🚀 *¡Sigue así!*"
        )
        
        try:
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=mensaje,
                parse_mode='Markdown'
            )
            logger.info(f"✅ Reporte enviado a {chat_id}")
        except Exception as e:
            logger.error(f"❌ Error enviando reporte: {e}")
    
    def run(self):
        """Ejecuta el bot"""
        logger.info("🚀 Iniciando bot Radar Maestro...")
        
        self.build_application()
        
        try:
            self.application.run_polling()
        except KeyboardInterrupt:
            logger.info("⏹️ Bot detenido por usuario")
        except Exception as e:
            logger.error(f"❌ Error en el bot: {e}")


def main():
    """Función principal"""
    bot = RadarBot()
    bot.run()


if __name__ == '__main__':
    main()

