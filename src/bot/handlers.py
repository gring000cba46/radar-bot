"""
Handlers de comandos para el bot de Telegram
Gestiona interacción con usuarios - v2 (rediseño completo)
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.models.database import init_db
from src.services.usuario_service import usuario_service
from src.services.combinada_service import combinada_service

logger = logging.getLogger(__name__)

ARG_TZ = ZoneInfo('America/Argentina/Buenos_Aires')

# ---------------------------------------------------------------------------
# Picks de demostración
# En producción estos vendrían de la API / algoritmo real.
# Las fechas se calculan a partir de "ahora" para que siempre sean próximas.
# ---------------------------------------------------------------------------

def _gen_picks():
    """Genera picks de demo con horarios relativos a ahora (UTC)."""
    now_utc = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    return [
        {
            'id': 1,
            'partido': 'Real Madrid vs Barcelona',
            'deporte': '⚽ Fútbol',
            'liga': 'La Liga',
            'fecha_hora_utc': now_utc + timedelta(hours=1, minutes=15),
            'mercado': 'Gana Local',
            'cuota': 2.10,
            'probabilidad_real': 50.0,
            'probabilidad_implicita': 47.6,
            'valor_pct': 3.2,
            'expected_value': 0.21,
            'confianza': 0.85,
            'nivel_valor': 'FUERTE',
        },
        {
            'id': 2,
            'partido': 'Atletico Madrid vs Sevilla',
            'deporte': '⚽ Fútbol',
            'liga': 'La Liga',
            'fecha_hora_utc': now_utc + timedelta(hours=1, minutes=15),
            'mercado': 'Ambos Anotan',
            'cuota': 1.90,
            'probabilidad_real': 56.0,
            'probabilidad_implicita': 52.6,
            'valor_pct': 2.1,
            'expected_value': 0.14,
            'confianza': 0.72,
            'nivel_valor': 'MODERADO',
        },
        {
            'id': 3,
            'partido': 'Man City vs Liverpool',
            'deporte': '⚽ Fútbol',
            'liga': 'Premier League',
            'fecha_hora_utc': now_utc + timedelta(hours=3, minutes=30),
            'mercado': 'Ambos Anotan',
            'cuota': 1.85,
            'probabilidad_real': 55.0,
            'probabilidad_implicita': 54.1,
            'valor_pct': 1.8,
            'expected_value': 0.15,
            'confianza': 0.70,
            'nivel_valor': 'MODERADO',
        },
        {
            'id': 4,
            'partido': 'Arsenal vs Chelsea',
            'deporte': '⚽ Fútbol',
            'liga': 'Premier League',
            'fecha_hora_utc': now_utc + timedelta(hours=5),
            'mercado': 'Gana Local',
            'cuota': 2.20,
            'probabilidad_real': 48.0,
            'probabilidad_implicita': 45.5,
            'valor_pct': 2.5,
            'expected_value': 0.18,
            'confianza': 0.75,
            'nivel_valor': 'MODERADO',
        },
        {
            'id': 5,
            'partido': 'Djokovic vs Alcaraz',
            'deporte': '🎾 Tenis',
            'liga': 'ATP Masters',
            'fecha_hora_utc': now_utc + timedelta(hours=6, minutes=45),
            'mercado': 'Gana Djokovic',
            'cuota': 1.95,
            'probabilidad_real': 53.0,
            'probabilidad_implicita': 51.3,
            'valor_pct': 0.5,
            'expected_value': 0.01,
            'confianza': 0.62,
            'nivel_valor': 'LEVE',
        },
        {
            'id': 6,
            'partido': 'Lakers vs Celtics',
            'deporte': '🏀 Basquet',
            'liga': 'NBA',
            'fecha_hora_utc': now_utc + timedelta(hours=8, minutes=20),
            'mercado': 'Gana Local',
            'cuota': 2.05,
            'probabilidad_real': 52.0,
            'probabilidad_implicita': 48.8,
            'valor_pct': 3.5,
            'expected_value': 0.25,
            'confianza': 0.80,
            'nivel_valor': 'FUERTE',
        },
    ]


def _hora_arg(dt_utc: datetime) -> str:
    """Convierte datetime UTC a hora Argentina formateada."""
    dt_arg = dt_utc.astimezone(ARG_TZ)
    return dt_arg.strftime('%H:%M ARG')


def _bloque_horario(dt_utc: datetime) -> str:
    """Clasifica un datetime UTC en un bloque horario relativo a ahora."""
    diff = (dt_utc - datetime.now(timezone.utc)).total_seconds() / 3600
    if diff < 0:
        return '🕐 Ya empezó / en curso'
    elif diff <= 2:
        return '⚡ Próximas 2 horas'
    elif diff <= 4:
        return '🕑 En 2 – 4 horas'
    elif diff <= 8:
        return '🕓 En 4 – 8 horas'
    else:
        return '🕗 Más de 8 horas'


def _emoji_nivel(nivel: str) -> str:
    return {'FUERTE': '🟢', 'MODERADO': '🟡', 'LEVE': '🔵'}.get(nivel, '⚪')


# ---------------------------------------------------------------------------
# Helpers de teclado
# ---------------------------------------------------------------------------

def _teclado_principal():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 PICKS", callback_data='picks'),
            InlineKeyboardButton("💎 VALOR FUERTE", callback_data='valor'),
        ],
        [
            InlineKeyboardButton("🎯 COMBINADA", callback_data='ver_combinada'),
            InlineKeyboardButton("💳 MI BANK", callback_data='bank'),
        ],
        [
            InlineKeyboardButton("📋 HISTORIAL", callback_data='historial'),
            InlineKeyboardButton("ℹ️ AYUDA", callback_data='ayuda'),
        ],
    ])


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

class BotHandlers:
    """Clase que agrupa todos los handlers del bot"""

    # ------------------------------------------------------------------
    # /start
    # ------------------------------------------------------------------
    @staticmethod
    async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Comando /start - Bienvenida y registro"""
        user = update.effective_user
        logger.info(f"Usuario iniciando: {user.id} - {user.first_name}")

        # Registrar / obtener usuario
        usuario_service.obtener_o_crear(str(user.id), user.first_name)

        await update.message.reply_text(
            f"¡Hola {user.first_name}! 👋\n\n"
            "Bienvenido a *Radar Maestro* 🎯\n"
            "Bot inteligente de análisis de cuotas deportivas\n\n"
            "Detectamos valor donde las casas se equivocan.\n"
            "Maximizá tu ROI con análisis estadístico.\n\n"
            "Elegí una opción:",
            reply_markup=_teclado_principal(),
            parse_mode='Markdown',
        )

    # ------------------------------------------------------------------
    # /picks
    # ------------------------------------------------------------------
    @staticmethod
    async def cmd_picks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Comando /picks - Picks agrupados por horario y liga"""
        picks = _gen_picks()
        picks.sort(key=lambda p: p['fecha_hora_utc'])

        # Agrupar por bloque horario, luego por liga
        bloques: dict[str, dict[str, list]] = {}
        for p in picks:
            bloque = _bloque_horario(p['fecha_hora_utc'])
            liga = f"{p['deporte']} — {p['liga']}"
            bloques.setdefault(bloque, {}).setdefault(liga, []).append(p)

        lines = ["📊 *PICKS DEL DÍA*\n"]
        keyboards: list[list] = []

        for bloque, ligas in bloques.items():
            lines.append(f"\n{'─' * 30}")
            lines.append(f"*{bloque}*")
            for liga, ps in ligas.items():
                lines.append(f"\n*{liga}*")
                for p in ps:
                    hora = _hora_arg(p['fecha_hora_utc'])
                    emoji = _emoji_nivel(p['nivel_valor'])
                    lines.append(
                        f"{emoji} *{p['partido']}*\n"
                        f"🕐 {hora}  |  Mercado: {p['mercado']}\n"
                        f"💰 Cuota: {p['cuota']}  |  Valor: +{p['valor_pct']}%\n"
                        f"🎯 Confianza: {int(p['confianza'] * 100)}%  |  EV: +{p['expected_value']:.2f}"
                    )
                    keyboards.append([
                        InlineKeyboardButton(
                            f"➕ A COMBINADA — {p['partido']}",
                            callback_data=f"add_comb_{p['id']}",
                        )
                    ])

        lines.append("\n\n💡 Tocá ➕ para agregar un pick a tu Combinada")
        keyboards.append([
            InlineKeyboardButton("🎯 Ver mi COMBINADA", callback_data='ver_combinada'),
            InlineKeyboardButton("🔙 Menú", callback_data='menu'),
        ])

        msg = update.message or update.callback_query.message
        await msg.reply_text(
            '\n'.join(lines),
            reply_markup=InlineKeyboardMarkup(keyboards),
            parse_mode='Markdown',
        )

    # ------------------------------------------------------------------
    # /valor
    # ------------------------------------------------------------------
    @staticmethod
    async def cmd_valor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Picks con valor fuerte, ordenados por horario ascendente"""
        picks = _gen_picks()
        # Solo valor FUERTE y MODERADO, orden ascendente por hora
        valor_picks = sorted(
            [p for p in picks if p['nivel_valor'] in ('FUERTE', 'MODERADO')],
            key=lambda p: p['fecha_hora_utc'],
        )

        lines = [
            "💎 *VALOR FUERTE*\n",
            "_(Oportunidades con prob. real > implícita, ordenadas por horario)_\n",
        ]
        keyboards: list[list] = []

        if not valor_picks:
            lines.append("⚠️ Sin picks de valor en este momento.\nVolvé más tarde.")
        else:
            for p in valor_picks:
                hora = _hora_arg(p['fecha_hora_utc'])
                emoji = _emoji_nivel(p['nivel_valor'])
                lines.append(
                    f"\n{emoji} *{p['partido']}*\n"
                    f"🕐 {hora}  |  {p['deporte']} — {p['liga']}\n"
                    f"Mercado: {p['mercado']}\n"
                    f"💰 Cuota: {p['cuota']}  |  Valor: +{p['valor_pct']}%\n"
                    f"Prob. Real: {p['probabilidad_real']}%  |  EV: +{p['expected_value']:.2f}\n"
                    f"🎯 Confianza: {int(p['confianza'] * 100)}%"
                )
                keyboards.append([
                    InlineKeyboardButton(
                        f"➕ A COMBINADA — {p['partido']}",
                        callback_data=f"add_comb_{p['id']}",
                    )
                ])

        lines.append("\n\n🔔 Recibirás alerta 30 min antes de cada partido con valor")
        keyboards.append([
            InlineKeyboardButton("🎯 Ver mi COMBINADA", callback_data='ver_combinada'),
            InlineKeyboardButton("🔙 Menú", callback_data='menu'),
        ])

        msg = update.message or update.callback_query.message
        await msg.reply_text(
            '\n'.join(lines),
            reply_markup=InlineKeyboardMarkup(keyboards),
            parse_mode='Markdown',
        )

    # ------------------------------------------------------------------
    # /bank
    # ------------------------------------------------------------------
    @staticmethod
    async def cmd_bank(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Muestra el estado del bank del usuario"""
        user = update.effective_user
        datos = usuario_service.obtener(str(user.id))

        if not datos:
            datos = usuario_service.obtener_o_crear(str(user.id), user.first_name)

        bank_actual = datos['bank_actual']
        bank_inicial = datos['bank_inicial']
        ganancia = bank_actual - bank_inicial
        ganancia_str = f"+${ganancia:,.2f}" if ganancia >= 0 else f"-${abs(ganancia):,.2f}"
        roi_str = f"+{datos['roi']:.1f}%" if datos['roi'] >= 0 else f"{datos['roi']:.1f}%"
        apuestas = datos['apuestas_totales']
        ganadas = datos['apuestas_ganadas']
        perdidas = apuestas - ganadas
        tasa = f"{(ganadas / apuestas * 100):.1f}%" if apuestas > 0 else "—"

        text = (
            "💳 *MI BANK*\n\n"
            f"💰 Saldo actual:   *${bank_actual:,.2f}*\n"
            f"📥 Bank inicial:    ${bank_inicial:,.2f}\n"
            f"📈 Ganancia:       {ganancia_str}\n"
            f"📊 ROI:             {roi_str}\n\n"
            f"🎰 Apuestas totales: {apuestas}\n"
            f"✅ Ganadas:  {ganadas}   ❌ Perdidas: {perdidas}\n"
            f"🎯 Tasa de acierto: {tasa}"
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📋 Historial combinadas", callback_data='historial'),
            ],
            [
                InlineKeyboardButton("🔙 Menú", callback_data='menu'),
            ],
        ])

        msg = update.message or update.callback_query.message
        await msg.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')

    # ------------------------------------------------------------------
    # /combinada  (ver combinada actual + confirmar/cancelar)
    # ------------------------------------------------------------------
    @staticmethod
    async def cmd_ver_combinada(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Muestra la combinada actual del usuario"""
        seleccion = context.user_data.get('combinada_picks', [])
        msg = update.message or update.callback_query.message

        if not seleccion:
            await msg.reply_text(
                "🎯 *COMBINADA*\n\n"
                "Aún no agregaste ningún pick.\n"
                "Andá a 📊 PICKS o 💎 VALOR FUERTE y usá ➕ para agregar.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("📊 Ver Picks", callback_data='picks'),
                    InlineKeyboardButton("🔙 Menú", callback_data='menu'),
                ]]),
                parse_mode='Markdown',
            )
            return

        cuota_total = 1.0
        prob_total = 1.0
        lines = ["🎯 *TU COMBINADA*\n"]

        for i, p in enumerate(seleccion, 1):
            cuota_total = round(cuota_total * p['cuota'], 4)
            prob_total = round(prob_total * (p['probabilidad_real'] / 100), 4)
            hora = _hora_arg(p['fecha_hora_utc'])
            lines.append(
                f"{i}. *{p['partido']}*\n"
                f"   🕐 {hora} | {p['liga']}\n"
                f"   Mercado: {p['mercado']} | Cuota: {p['cuota']}"
            )

        lines.append(
            f"\n{'─' * 28}\n"
            f"💰 *Cuota combinada:* {cuota_total:.2f}\n"
            f"📊 *Probabilidad combinada:* {prob_total * 100:.1f}%"
        )

        # Construir teclado: quitar picks + confirmar + cancelar
        remove_btns = [
            [InlineKeyboardButton(f"❌ Quitar #{i} — {p['partido']}", callback_data=f"rm_comb_{p['id']}")]
            for i, p in enumerate(seleccion, 1)
        ]
        action_btns = [
            [
                InlineKeyboardButton("✅ CONFIRMAR", callback_data='confirmar_combinada'),
                InlineKeyboardButton("❌ CANCELAR", callback_data='cancelar_combinada'),
            ],
            [InlineKeyboardButton("➕ Agregar más picks", callback_data='picks')],
        ]

        await msg.reply_text(
            '\n'.join(lines),
            reply_markup=InlineKeyboardMarkup(remove_btns + action_btns),
            parse_mode='Markdown',
        )

    # ------------------------------------------------------------------
    # /historial
    # ------------------------------------------------------------------
    @staticmethod
    async def cmd_historial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Muestra historial de combinadas del usuario"""
        user = update.effective_user
        historial = combinada_service.obtener_historial(str(user.id), limite=10)

        msg = update.message or update.callback_query.message

        if not historial:
            await msg.reply_text(
                "📋 *HISTORIAL*\n\nTodavía no tenés combinadas registradas.\n"
                "¡Armá tu primera combinada y apostá! 🎯",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🎯 Armar COMBINADA", callback_data='ver_combinada'),
                    InlineKeyboardButton("🔙 Menú", callback_data='menu'),
                ]]),
                parse_mode='Markdown',
            )
            return

        lines = ["📋 *HISTORIAL DE COMBINADAS*\n"]
        for c in historial:
            res_emoji = {'GANADA': '✅', 'PERDIDA': '❌', 'PENDIENTE': '⏳'}.get(c['resultado'], '❓')
            gan_str = ''
            if c['ganancia'] is not None:
                gan_str = f"+${c['ganancia']:.2f}" if c['ganancia'] >= 0 else f"${c['ganancia']:.2f}"
            fecha_str = c.get('finalizado') or c['creado']
            picks_resumen = ', '.join(
                p['partido'] for p in c['picks_data']
            ) if c['picks_data'] else '—'
            lines.append(
                f"{res_emoji} *#{c['id']}* — {fecha_str}\n"
                f"Picks: {picks_resumen}\n"
                f"Monto: ${c['monto']:.2f}  |  Cuota: {c['cuota_total']:.2f}\n"
                f"Resultado: *{c['resultado']}*  {gan_str}\n"
            )

        await msg.reply_text(
            '\n'.join(lines),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Menú", callback_data='menu'),
            ]]),
            parse_mode='Markdown',
        )

    # ------------------------------------------------------------------
    # /ayuda
    # ------------------------------------------------------------------
    @staticmethod
    async def cmd_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Información y ayuda"""
        ayuda_text = (
            "ℹ️ *INFORMACIÓN — RADAR MAESTRO*\n\n"

            "🎯 *¿QUÉ SOMOS?*\n"
            "Bot inteligente de detección de valor en cuotas deportivas.\n"
            "Usamos algoritmos estadísticos para encontrar oportunidades donde las casas se equivocan.\n\n"

            "📚 *CONCEPTOS CLAVE*\n\n"
            "*VALOR*\nCuando tu prob. real > prob. implícita de la cuota.\n"
            "Ejemplo: Prob. real 50% y Cuota 2.10 (implícita 47.6%) → Valor +3.2%\n\n"

            "*CUOTA COMBINADA*\nMultiplicación de todas las cuotas individuales.\n\n"

            "*PROBABILIDAD COMBINADA*\nMultiplicación de todas las probabilidades reales.\n\n"

            "*ROI*\nGanancia como % del capital inicial.\n\n"

            "📞 *COMANDOS*\n"
            "/start — Menú principal\n"
            "/picks — Ver todos los picks\n"
            "/valor — Solo valor fuerte\n"
            "/bank — Tu bankroll\n"
            "/historial — Historial de combinadas\n"
            "/ayuda — Esta pantalla\n\n"

            "⚠️ *Apostá solo lo que estés dispuesto a perder.*"
        )

        msg = update.message or update.callback_query.message
        await msg.reply_text(
            ayuda_text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Menú", callback_data='menu'),
            ]]),
            parse_mode='Markdown',
        )

    # ------------------------------------------------------------------
    # Callback handler (botones inline)
    # ------------------------------------------------------------------
    @staticmethod
    async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Maneja todos los callbacks de botones inline"""
        query = update.callback_query
        await query.answer()
        data = query.data

        # ---- menú principal ----
        if data == 'menu':
            await query.message.reply_text(
                "Menú principal:",
                reply_markup=_teclado_principal(),
            )

        # ---- picks ----
        elif data == 'picks':
            await BotHandlers.cmd_picks(update, context)

        # ---- valor fuerte ----
        elif data == 'valor':
            await BotHandlers.cmd_valor(update, context)

        # ---- bank ----
        elif data == 'bank':
            await BotHandlers.cmd_bank(update, context)

        # ---- historial ----
        elif data == 'historial':
            await BotHandlers.cmd_historial(update, context)

        # ---- ver combinada ----
        elif data == 'ver_combinada':
            await BotHandlers.cmd_ver_combinada(update, context)

        # ---- agregar pick a combinada ----
        elif data.startswith('add_comb_'):
            pick_id = int(data.split('_')[-1])
            picks = _gen_picks()
            pick = next((p for p in picks if p['id'] == pick_id), None)
            if pick:
                combinada = context.user_data.setdefault('combinada_picks', [])
                if any(p['id'] == pick_id for p in combinada):
                    await query.answer("Ya agregaste ese pick ✓", show_alert=False)
                else:
                    combinada.append(pick)
                    await query.message.reply_text(
                        f"✅ *{pick['partido']}* agregado a tu combinada.\n"
                        f"Total de picks: {len(combinada)}\n\n"
                        "Seguí agregando o tocá 🎯 COMBINADA para confirmar.",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🎯 Ver COMBINADA", callback_data='ver_combinada'),
                            InlineKeyboardButton("➕ Más Picks", callback_data='picks'),
                        ]]),
                        parse_mode='Markdown',
                    )

        # ---- quitar pick de combinada ----
        elif data.startswith('rm_comb_'):
            pick_id = int(data.split('_')[-1])
            combinada = context.user_data.get('combinada_picks', [])
            context.user_data['combinada_picks'] = [
                p for p in combinada if p['id'] != pick_id
            ]
            await BotHandlers.cmd_ver_combinada(update, context)

        # ---- confirmar combinada ----
        elif data == 'confirmar_combinada':
            seleccion = context.user_data.get('combinada_picks', [])
            if not seleccion:
                await query.message.reply_text("No tenés picks en tu combinada.")
                return

            user = update.effective_user
            datos_usuario = usuario_service.obtener(str(user.id))
            if not datos_usuario:
                datos_usuario = usuario_service.obtener_o_crear(str(user.id), user.first_name)

            # Monto por defecto: 5% del bank actual
            monto = round(datos_usuario['bank_actual'] * 0.05, 2)

            combinada = combinada_service.crear(str(user.id), seleccion, monto)

            cuota_total = combinada['cuota_total']
            prob_total = combinada['prob_total']
            ganancia_potencial = round(monto * (cuota_total - 1), 2)

            context.user_data['combinada_picks'] = []  # limpiar

            await query.message.reply_text(
                f"✅ *COMBINADA CONFIRMADA*\n\n"
                f"Picks: {combinada['picks_count']}\n"
                f"💰 Monto apostado: ${monto:.2f}\n"
                f"🎰 Cuota combinada: {cuota_total:.2f}\n"
                f"📊 Probabilidad: {prob_total * 100:.1f}%\n"
                f"💵 Ganancia potencial: ${ganancia_potencial:.2f}\n\n"
                f"*ID combinada: #{combinada['id']}*\n\n"
                "¡Mucha suerte! 🍀\n"
                "Podés ver el resultado en 📋 HISTORIAL.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("📋 Historial", callback_data='historial'),
                    InlineKeyboardButton("🔙 Menú", callback_data='menu'),
                ]]),
                parse_mode='Markdown',
            )

        # ---- cancelar combinada ----
        elif data == 'cancelar_combinada':
            context.user_data['combinada_picks'] = []
            await query.message.reply_text(
                "❌ *Combinada cancelada.*\n\nTus picks fueron descartados.",
                reply_markup=_teclado_principal(),
                parse_mode='Markdown',
            )

        # ---- ayuda ----
        elif data == 'ayuda':
            await BotHandlers.cmd_ayuda(update, context)

    # ------------------------------------------------------------------
    # Job: alertas 30 min antes de partidos con valor fuerte
    # ------------------------------------------------------------------
    @staticmethod
    async def job_alertas_30min(context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Se ejecuta cada minuto.
        Envía alerta a todos los usuarios registrados cuando un pick con
        valor fuerte está a 30 minutos (±1 min) de comenzar.
        """
        from src.models.database import SessionLocal, Usuario as UsuarioModel, Pick as PickModel

        ahora_utc = datetime.now(timezone.utc)
        ventana_inicio = ahora_utc + timedelta(minutes=29)
        ventana_fin = ahora_utc + timedelta(minutes=31)

        picks_alerta = [
            p for p in _gen_picks()
            if (
                p['nivel_valor'] in ('FUERTE', 'MODERADO')
                and ventana_inicio <= p['fecha_hora_utc'] <= ventana_fin
            )
        ]

        if not picks_alerta:
            return

        db = SessionLocal()
        try:
            usuarios = db.query(UsuarioModel).filter(UsuarioModel.activo == True).all()
            telegram_ids = [u.telegram_id for u in usuarios]
        finally:
            db.close()

        for pick in picks_alerta:
            hora = _hora_arg(pick['fecha_hora_utc'])
            texto = (
                f"🚨 *VALOR FUERTE EN 30 MIN*\n\n"
                f"*{pick['partido']}*\n"
                f"🕐 {hora}  |  {pick['liga']}\n"
                f"Mercado: {pick['mercado']}\n"
                f"💰 Cuota: {pick['cuota']}  |  Valor: +{pick['valor_pct']}%\n\n"
                f"⚠️ Apostá solo lo que estés dispuesto a perder."
            )
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "➕ Agregar a COMBINADA",
                    callback_data=f"add_comb_{pick['id']}",
                )
            ]])

            for tid in telegram_ids:
                try:
                    await context.bot.send_message(
                        chat_id=tid,
                        text=texto,
                        reply_markup=keyboard,
                        parse_mode='Markdown',
                    )
                except Exception as e:
                    logger.warning(f"No se pudo enviar alerta a {tid}: {e}")


