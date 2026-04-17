"""
Handlers de comandos para el bot de Telegram
Gestiona interacción con usuarios
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BotHandlers:
    """Clase que agrupa todos los handlers del bot"""
    
    @staticmethod
    async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Comando /start - Bienvenida y registro"""
        user = update.effective_user
        logger.info(f"Usuario iniciando: {user.id} - {user.first_name}")
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Picks", callback_data='picks'),
                InlineKeyboardButton("📈 Rendimiento", callback_data='rendimiento')
            ],
            [
                InlineKeyboardButton("💎 Valor", callback_data='valor'),
                InlineKeyboardButton("💰 Bank", callback_data='bank')
            ],
            [
                InlineKeyboardButton("ℹ️ Ayuda", callback_data='ayuda')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"¡Hola {user.first_name}! 👋\n\n"
            "Bienvenido a **Radar Maestro**\n"
            "Bot inteligente de análisis de cuotas deportivas\n\n"
            "🎯 **Nuestro objetivo:**\n"
            "Detectar valor donde las casas se equivocan\n"
            "Maximizar tu ROI con análisis inteligente\n\n"
            "Elige una opción:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def cmd_picks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Comando /picks - Mostrar picks del día"""
        logger.info(f"Usuario pidiendo picks: {update.effective_user.id}")
        
        picks_text = (
            "📊 **PICKS DEL DÍA**\n\n"
            
            "🔴 **FÚTBOL - LA LIGA**\n"
            "Real Madrid vs Barcelona\n"
            "💰 Cuota: 2.10 | Mercado: Gana Local\n"
            "✅ Valor: +3.2% | EV: +0.21\n"
            "🎯 Confianza: FUERTE\n"
            "📝 Análisis: Prob real 50% vs implicita 47.6%\n\n"
            
            "🟡 **FÚTBOL - PREMIER**\n"
            "Man City vs Liverpool\n"
            "💰 Cuota: 1.85 | Mercado: Ambos Anotan\n"
            "✅ Valor: +1.8% | EV: +0.15\n"
            "🎯 Confianza: MEDIA\n"
            "📝 Análisis: Historial de 4 años en esta matchup\n\n"
            
            "🟢 **TENIS - ATP**\n"
            "Djokovic vs Alcaraz\n"
            "💰 Cuota: 1.95 | Mercado: Gana Djokovic\n"
            "✅ Valor: +0.5% | EV: +0.01\n"
            "🎯 Confianza: DÉBIL\n"
            "📝 Análisis: Valor marginal, solo si quieres jugar\n\n"
            
            "ℹ️ Usa /valor para solo ver oportunidades con valor real"
        )
        
        await update.message.reply_text(picks_text, parse_mode='Markdown')
    
    @staticmethod
    async def cmd_rendimiento(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Comando /rendimiento - Mostrar rendimiento del usuario"""
        user_id = update.effective_user.id
        logger.info(f"Usuario pidiendo rendimiento: {user_id}")
        
        rendimiento_text = (
            "📈 **TU RENDIMIENTO**\n\n"
            
            "💰 **BANKROLL**\n"
            "Saldo Actual: $1,150.50\n"
            "Ganancia: +$150.50\n"
            "ROI: +15.05%\n\n"
            
            "📊 **APUESTAS**\n"
            "Total Apostado: 24\n"
            "Aciertos: 15 ✅\n"
            "Fallos: 9 ❌\n"
            "Tasa de Acierto: 62.5%\n"
            "Yield: +2.3%\n\n"
            
            "🎯 **ÚLTIMOS 7 DÍAS**\n"
            "Apuestas: 8\n"
            "ROI: +18.5%\n"
            "Mejora: +3.5% vs promedio\n\n"
            
            "📉 **ÚLTIMOS 30 DÍAS**\n"
            "Apuestas: 24\n"
            "ROI: +15.05%\n"
            "Ganancia: +$150.50\n\n"
            
            "💡 *Tu tasa de acierto está sobre el promedio del mercado. ¡Sigue así!*"
        )
        
        await update.message.reply_text(rendimiento_text, parse_mode='Markdown')
    
    @staticmethod
    async def cmd_valor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Comando /valor - Solo picks con valor real"""
        logger.info(f"Usuario pidiendo alertas de valor: {update.effective_user.id}")
        
        valor_text = (
            "💎 **ALERTAS DE VALOR**\n"
            "*(Solo oportunidades con probabilidad real > implícita)*\n\n"
            
            "🟢 **VALOR FUERTE** | +3.2%\n"
            "Real Madrid vs Barcelona\n"
            "Mercado: Gana Local\n"
            "Cuota: 2.10 | Prob Real: 50% | Prob Implicita: 47.6%\n"
            "Expected Value: +0.21\n"
            "Recomendación: ✅ APOSTAR\n\n"
            
            "🟡 **VALOR MEDIO** | +1.8%\n"
            "Man City vs Liverpool\n"
            "Mercado: Ambos Anotan\n"
            "Cuota: 1.85 | Prob Real: 55% | Prob Implicita: 54%\n"
            "Expected Value: +0.15\n"
            "Recomendación: ✅ CONSIDERAR\n\n"
            
            "⚠️ Sin más oportunidades de valor en este momento.\n"
            "Esperando nuevos análisis...\n\n"
            
            "🔔 Te notificaré cuando detecte nuevo valor"
        )
        
        await update.message.reply_text(valor_text, parse_mode='Markdown')
    
    @staticmethod
    async def cmd_bank(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Comando /bank - Gestionar bankroll"""
        user_id = update.effective_user.id
        logger.info(f"Usuario accediendo a bank: {user_id}")
        
        keyboard = [
            [
                InlineKeyboardButton("➕ Recargar", callback_data='recargar'),
                InlineKeyboardButton("📊 Historial", callback_data='historial_bank')
            ],
            [
                InlineKeyboardButton("🎰 Apuestas Activas", callback_data='apuestas_activas')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        bank_text = (
            "💰 **TU BANKROLL**\n\n"
            
            "**RESUMEN**\n"
            "Saldo: $1,150.50\n"
            "Inicial: $1,000.00\n"
            "Ganancia: +$150.50 (+15.05%)\n\n"
            
            "**DISTRIBUCIÓN**\n"
            "En Juego: $100.00 (8.7%)\n"
            "Disponible: $1,050.50 (91.3%)\n\n"
            
            "**ÚLTIMOS MOVIMIENTOS**\n"
            "✅ +$50.00 - Apuesta ganada (RM vs Barcelona)\n"
            "❌ -$25.00 - Apuesta perdida (Man City)\n"
            "✅ +$30.00 - Apuesta ganada (Djokovic)\n"
        )
        
        await update.message.reply_text(
            bank_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    @staticmethod
    async def cmd_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Comando /ayuda - Información y ayuda"""
        ayuda_text = (
            "ℹ️ **INFORMACIÓN - RADAR MAESTRO**\n\n"
            
            "🎯 **¿QUÉ SOMOS?**\n"
            "Bot inteligente especializado en detección de valor en cuotas deportivas\n"
            "Utilizamos algoritmos avanzados para identificar oportunidades donde las casas se equivocan\n\n"
            
            "📚 **CONCEPTOS CLAVE**\n\n"
            
            "**VALOR**\n"
            "Cuando la probabilidad REAL es mayor que la probabilidad implícita en la cuota\n"
            "Fórmula: Si P(Real) > 1/Cuota → HAY VALOR\n"
            "Ejemplo: Si Real=50% y Cuota=2.10 (Implicita=47.6%) → Valor de +3.2%\n\n"
            
            "**EXPECTED VALUE (EV)**\n"
            "Ganancia esperada a largo plazo por apuesta\n"
            "EV = (P(Real) × Cuota) - 1\n"
            "Si EV > 0 → Apostar genera ganancias en el largo plazo\n\n"
            
            "**YIELD**\n"
            "Ganancia como porcentaje del total apostado\n"
            "Yield = Ganancia / Total Apostado × 100\n"
            "Nuestro objetivo: Yield > 2% (profesional)\n\n"
            
            "**ROI**\n"
            "Return on Investment - Ganancia como % del capital inicial\n"
            "ROI = Ganancia / Capital Inicial × 100\n\n"
            
            "💡 **TIPS PARA GANAR**\n"
            "✅ Solo apuesta cuando hay VALOR detectado\n"
            "✅ Usa tamaños de apuesta consistentes\n"
            "✅ No apuestes más del 5% de tu bank por apuesta\n"
            "✅ Paciencia: el valor se realiza a largo plazo\n"
            "✅ Trackea tus resultados siempre\n\n"
            
            "📞 **COMANDOS DISPONIBLES**\n"
            "/picks - Ver picks del día\n"
            "/valor - Solo oportunidades con valor\n"
            "/rendimiento - Tu estadísticas\n"
            "/bank - Gestionar tu bankroll\n"
            "/ayuda - Esta información\n\n"
            
            "🔗 *Panel de control: https://radar-bot.herokuapp.com*"
        )
        
        await update.message.reply_text(ayuda_text, parse_mode='Markdown')
    
    @staticmethod
    async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Maneja callbacks de botones"""
        query = update.callback_query
        await query.answer()
        
        callbacks = {
            'picks': BotHandlers.cmd_picks,
            'rendimiento': BotHandlers.cmd_rendimiento,
            'valor': BotHandlers.cmd_valor,
            'bank': BotHandlers.cmd_bank,
            'ayuda': BotHandlers.cmd_ayuda,
        }
        
        handler = callbacks.get(query.data)
        if handler:
            await handler(update, context)

