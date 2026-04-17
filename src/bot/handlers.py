"""
Handlers del bot de Telegram - Radar Maestro
"""

import logging
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from src.core.picks_service import picks_service
from src.models.database import (
    Apuesta, Movimiento, SessionLocal,
    get_or_create_usuario,
)

logger = logging.getLogger(__name__)

DISCLAIMER = "\n\n⚠️ _Apuesta solo lo que estés dispuesto a perder._"
WAITING_BANKROLL = 1
WAITING_BET_AMOUNT = 2
MAX_COMBO_SIZE = 5  # Maximum picks allowed in a combo


def _menu_principal():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚽ Fútbol",     callback_data="deporte:Fútbol"),
            InlineKeyboardButton("🎾 Tenis",      callback_data="deporte:Tenis"),
            InlineKeyboardButton("🏀 Básquet",    callback_data="deporte:Basquetbol"),
        ],
        [
            InlineKeyboardButton("📈 Rendimiento", callback_data="rendimiento"),
            InlineKeyboardButton("💰 Bank",        callback_data="bank"),
        ],
        [
            InlineKeyboardButton("🎰 ARMAR COMBO",  callback_data="combo:inicio"),
        ],
        [
            InlineKeyboardButton("💎 VALOR FUERTE", callback_data="valor"),
        ],
    ])


def _get_usuario(telegram_id, nombre=""):
    db = SessionLocal()
    try:
        return get_or_create_usuario(db, str(telegram_id), nombre)
    finally:
        db.close()


def _set_bankroll(telegram_id, monto):
    db = SessionLocal()
    try:
        u = get_or_create_usuario(db, str(telegram_id))
        u.saldo_inicial = monto
        u.saldo = monto
        u.ultima_actividad = datetime.utcnow()
        db.commit()
        db.refresh(u)
        return u
    finally:
        db.close()


def _registrar_apuesta(telegram_id, pick, monto):
    db = SessionLocal()
    try:
        u = get_or_create_usuario(db, str(telegram_id))
        ap = Apuesta(
            usuario_id=str(telegram_id),
            partido=pick.get("evento", ""),
            mercado="{} - {}".format(pick.get("tipo_mercado", ""), pick.get("opcion", "")),
            monto=monto,
            cuota=pick.get("cuota", 0.0),
            resultado="PENDIENTE",
        )
        ant = u.saldo
        u.saldo = max(0.0, u.saldo - monto)
        db.add(ap)
        db.add(Movimiento(
            usuario_id=str(telegram_id), tipo="APUESTA", monto=-monto,
            saldo_anterior=ant, saldo_nuevo=u.saldo,
            descripcion="Apuesta: {}".format(pick.get("evento", "")),
        ))
        db.commit()
        db.refresh(ap)
        return ap
    finally:
        db.close()


def _marcar_resultado(apuesta_id, telegram_id, ganada):
    db = SessionLocal()
    try:
        ap = db.query(Apuesta).filter(
            Apuesta.id == apuesta_id,
            Apuesta.usuario_id == str(telegram_id),
        ).first()
        if not ap:
            return {"ok": False, "msg": "Apuesta no encontrada"}
        if ap.resultado != "PENDIENTE":
            return {"ok": False, "msg": "Ya tiene resultado"}
        u = get_or_create_usuario(db, str(telegram_id))
        ant = u.saldo
        if ganada:
            ganancia = ap.monto * (ap.cuota - 1)
            ap.ganancia = ganancia
            ap.resultado = "GANADO"
            u.saldo += ap.monto + ganancia
        else:
            ap.ganancia = -ap.monto
            ap.resultado = "PERDIDO"
        ap.fecha_resultado = datetime.utcnow()
        db.add(Movimiento(
            usuario_id=str(telegram_id), tipo="RESULTADO",
            monto=ap.ganancia, saldo_anterior=ant, saldo_nuevo=u.saldo,
            descripcion="Resultado {}: {}".format("GANADO" if ganada else "PERDIDO", ap.partido),
        ))
        db.commit()
        return {"ok": True, "ganada": ganada, "ganancia": ap.ganancia, "saldo": u.saldo}
    finally:
        db.close()


def _get_apuestas(telegram_id):
    db = SessionLocal()
    try:
        return (db.query(Apuesta)
                .filter(Apuesta.usuario_id == str(telegram_id))
                .order_by(Apuesta.fecha_apuesta.desc())
                .limit(10).all())
    finally:
        db.close()


def _stats(telegram_id):
    db = SessionLocal()
    try:
        u = get_or_create_usuario(db, str(telegram_id))
        aps = db.query(Apuesta).filter(Apuesta.usuario_id == str(telegram_id)).all()
        total = len(aps)
        ganadas = sum(1 for a in aps if a.resultado == "GANADO")
        perdidas = sum(1 for a in aps if a.resultado == "PERDIDO")
        apost = sum(a.monto for a in aps)
        ganancia_total = sum(a.ganancia for a in aps)
        tasa = (ganadas / total * 100) if total > 0 else 0.0
        yld = (ganancia_total / apost * 100) if apost > 0 else 0.0
        return {
            "saldo": u.saldo, "saldo_inicial": u.saldo_inicial,
            "ganancia": u.saldo - u.saldo_inicial, "roi": u.roi,
            "total": total, "ganadas": ganadas, "perdidas": perdidas,
            "pendientes": total - ganadas - perdidas,
            "tasa_acierto": tasa, "yield": yld,
            "bank_configurado": u.bank_configurado,
        }
    finally:
        db.close()


def _fmt_pick(pick, bankroll=0.0):
    cap = picks_service.calcular_capital_recomendado(
        pick["prob_real"], bankroll, pick.get("cuota", 2.0)
    )
    cap_s = "${:,.2f}".format(cap) if bankroll > 0 else "- (configura /bank)"
    hora = pick.get("hora", "")
    hora_s = " ({})".format(hora) if hora else ""
    return "\n".join([
        "🏟 *{}*{}".format(pick["evento"], hora_s),
        "🏆 {}".format(pick.get("liga", "")),
        "📌 Mercado: {} - *{}*".format(pick.get("tipo_mercado", ""), pick.get("opcion", "")),
        "💰 Cuota: *{}*".format(pick["cuota"]),
        "📊 Probabilidad: *{:.0%}*".format(pick["prob_real"]),
        "💵 Capital recomendado: *{}*".format(cap_s),
    ])


async def _reply(update, texto, keyboard=None, parse_mode="Markdown"):
    q = getattr(update, "callback_query", None)
    if q:
        try:
            await q.edit_message_text(texto, reply_markup=keyboard, parse_mode=parse_mode)
        except Exception:
            await q.message.reply_text(texto, reply_markup=keyboard, parse_mode=parse_mode)
    elif update.message:
        await update.message.reply_text(texto, reply_markup=keyboard, parse_mode=parse_mode)


class BotHandlers:

    @staticmethod
    async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        _get_usuario(user.id, user.first_name or "")
        await update.message.reply_text(
            "¡Hola {}! 👋\n\n"
            "*Bienvenido a Radar Maestro* 🎯\n"
            "Detecto valor donde las casas se equivocan.\n\n"
            "Elige una opción:".format(user.first_name),
            reply_markup=_menu_principal(), parse_mode="Markdown"
        )

    @staticmethod
    async def cmd_bank(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.effective_user
        args = context.args
        if args:
            try:
                monto = float(args[0].replace(",", "."))
            except ValueError:
                await update.message.reply_text(
                    "❌ Ingresa un número válido. Ej: `/bank 1000`", parse_mode="Markdown"
                )
                return ConversationHandler.END
            u = _set_bankroll(user.id, monto)
            await update.message.reply_text(
                "✅ *Bankroll configurado:* ${:,.2f}\n\n"
                "A partir de ahora calcularé el capital recomendado para cada pick.{}".format(
                    u.saldo, DISCLAIMER
                ),
                parse_mode="Markdown"
            )
            return ConversationHandler.END
        s = _stats(user.id)
        if not s["bank_configurado"]:
            await update.message.reply_text(
                "💰 *Configura tu Bankroll*\n\nIngresa tu capital inicial (ej: `1000`):",
                parse_mode="Markdown"
            )
            return WAITING_BANKROLL
        await BotHandlers._show_bank_msg(update.message, user.id)
        return ConversationHandler.END

    @staticmethod
    async def recibir_bankroll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        try:
            monto = float(update.message.text.replace(",", "."))
        except ValueError:
            await update.message.reply_text(
                "❌ Ingresa un número válido, ej: `1000`", parse_mode="Markdown"
            )
            return WAITING_BANKROLL
        u = _set_bankroll(update.effective_user.id, monto)
        await update.message.reply_text(
            "✅ *Bankroll configurado:* ${:,.2f}\n\nAhora calcularé el capital recomendado.{}".format(
                u.saldo, DISCLAIMER
            ),
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    @staticmethod
    def _bank_texto(user_id):
        s = _stats(user_id)
        gn = s["ganancia"]
        sg = "+" if gn >= 0 else ""
        return (
            "💰 *TU BANKROLL*\n\n"
            "Saldo actual: *${:,.2f}*\n"
            "Capital inicial: ${:,.2f}\n"
            "Ganancia: *{}${:,.2f}* ({}{}%)\n\n"
            "📊 *APUESTAS*\n"
            "Total: {} | ✅ {} | ❌ {} | ⏳ {}\n"
            "Tasa de acierto: {:.1f}%\n"
            "Yield: {:+.2f}%"
        ).format(
            s["saldo"], s["saldo_inicial"],
            sg, abs(gn), sg, abs(s["roi"]),
            s["total"], s["ganadas"], s["perdidas"], s["pendientes"],
            s["tasa_acierto"], s["yield"]
        ) + DISCLAIMER

    @staticmethod
    def _bank_keyboard():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Historial", callback_data="historial"),
             InlineKeyboardButton("🔄 Cambiar bank", callback_data="bank:cambiar")],
            [InlineKeyboardButton("◀️ Menú", callback_data="menu")],
        ])

    @staticmethod
    async def _show_bank_msg(message, user_id):
        await message.reply_text(
            BotHandlers._bank_texto(user_id),
            reply_markup=BotHandlers._bank_keyboard(),
            parse_mode="Markdown"
        )

    @staticmethod
    async def _show_bank_query(query, user_id):
        await query.edit_message_text(
            BotHandlers._bank_texto(user_id),
            reply_markup=BotHandlers._bank_keyboard(),
            parse_mode="Markdown"
        )

    @staticmethod
    async def cmd_rendimiento(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        s = _stats(update.effective_user.id)
        if not s["bank_configurado"]:
            await _reply(update, "⚠️ Primero configura tu bankroll con `/bank <monto>`")
            return
        gn = s["ganancia"]
        sg = "+" if gn >= 0 else ""
        texto = (
            "📈 *TU RENDIMIENTO*\n\n"
            "💰 Saldo: *${:,.2f}*\n"
            "📈 Ganancia: *{}${:,.2f}*\n"
            "🔄 ROI: *{}{:.2f}%*\n"
            "📊 Yield: *{:+.2f}%*\n\n"
            "🎯 *APUESTAS*\n"
            "Total: {}\n✅ Ganadas: {}\n❌ Perdidas: {}\n⏳ Pendientes: {}\n"
            "Tasa de acierto: {:.1f}%"
        ).format(
            s["saldo"], sg, abs(gn), sg, abs(s["roi"]), s["yield"],
            s["total"], s["ganadas"], s["perdidas"], s["pendientes"], s["tasa_acierto"]
        ) + DISCLAIMER
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Historial", callback_data="historial")],
            [InlineKeyboardButton("◀️ Menú", callback_data="menu")],
        ])
        await _reply(update, texto, kb)

    @staticmethod
    async def cmd_valor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        s = _stats(update.effective_user.id)
        br = s["saldo"] if s["bank_configurado"] else 0.0
        picks = picks_service.obtener_picks_valor_fuerte()
        if not picks:
            await _reply(
                update,
                "💎 *VALOR FUERTE*\n\n⚠️ Sin picks de valor fuerte en este momento." + DISCLAIMER
            )
            return
        partes = ["💎 *VALOR FUERTE*\n_(Valor > 5%)_\n"]
        for p in picks:
            partes.append("-" * 35)
            partes.append(_fmt_pick(p, br))
            partes.append("📈 Valor: *+{:.1f}%*".format(p["valor_pct"]))
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎰 ARMAR COMBO", callback_data="combo:inicio")],
            [InlineKeyboardButton("◀️ Menú", callback_data="menu")],
        ])
        await _reply(update, "\n".join(partes) + DISCLAIMER, kb)

    @staticmethod
    async def mostrar_picks_deporte(update, context, deporte):
        s = _stats(update.effective_user.id)
        br = s["saldo"] if s["bank_configurado"] else 0.0
        picks = picks_service.obtener_picks_deporte(deporte)
        emojis = {"Fútbol": "⚽", "Tenis": "🎾", "Basquetbol": "🏀"}
        em = emojis.get(deporte, "🏅")
        if not picks:
            await _reply(
                update,
                "{} *{}*\n\n⚠️ Sin picks válidos en este momento.".format(
                    em, deporte.upper()
                ) + DISCLAIMER
            )
            return
        partes = ["{} *{} - PICKS DEL DÍA*\n".format(em, deporte.upper())]
        grupos = {}
        for pk in picks:
            liga = pk.get("liga", "Sin liga")
            grupos.setdefault(liga, []).append(pk)
        for liga, lps in grupos.items():
            partes.append("\n🏆 *{}*".format(liga))
            for pk in lps:
                partes.append("-" * 35)
                partes.append(_fmt_pick(pk, br))
        botones = []
        for i, pk in enumerate(picks):
            botones.append([InlineKeyboardButton(
                "📌 Apostar: {} @ {}".format(pk.get("opcion", ""), pk["cuota"]),
                callback_data="apostar:{}:{}".format(i, deporte)
            )])
        botones.append([
            InlineKeyboardButton("🎰 ARMAR COMBO", callback_data="combo:inicio"),
            InlineKeyboardButton("◀️ Menú", callback_data="menu"),
        ])
        context.user_data["picks_{}".format(deporte)] = picks
        await _reply(update, "\n".join(partes) + DISCLAIMER, InlineKeyboardMarkup(botones))

    @staticmethod
    async def mostrar_historial(update, context):
        uid = update.effective_user.id
        aps = _get_apuestas(uid)
        if not aps:
            texto = "📋 *HISTORIAL*\n\nAún no tienes apuestas registradas."
        else:
            lineas = ["📋 *HISTORIAL DE APUESTAS* _(últimas 10)_\n"]
            icon_map = {"GANADO": "✅", "PERDIDO": "❌", "PENDIENTE": "⏳"}
            for ap in aps:
                status_icon = icon_map.get(ap.resultado, "⏳")
                gs = " (${:+.2f})".format(ap.ganancia) if ap.resultado != "PENDIENTE" else ""
                lineas.append("{} *{}*\n   ${:.2f} @ {}{}  -  {}".format(
                    status_icon, ap.partido, ap.monto, ap.cuota, gs,
                    ap.fecha_apuesta.strftime("%d/%m %H:%M")
                ))
            texto = "\n".join(lineas)
        pendientes = [ap for ap in aps if ap.resultado == "PENDIENTE"]
        bots = []
        for ap in pendientes[:5]:
            bots.append([
                InlineKeyboardButton(
                    "✅ Gané - {}".format(ap.partido[:25]),
                    callback_data="res:won:{}".format(ap.id)
                ),
                InlineKeyboardButton("❌ Perdí", callback_data="res:lost:{}".format(ap.id)),
            ])
        bots.append([InlineKeyboardButton("◀️ Menú", callback_data="menu")])
        await _reply(update, texto + DISCLAIMER, InlineKeyboardMarkup(bots))

    @staticmethod
    async def iniciar_combo(update, context):
        todos = picks_service.obtener_todos_picks()
        if not todos:
            await _reply(update, "⚠️ No hay picks disponibles para armar un combo.")
            return
        context.user_data["combo_sel"] = []
        context.user_data["combo_picks"] = todos
        await BotHandlers._show_combo_selector(update, context)

    @staticmethod
    async def _show_combo_selector(update, context):
        todos = context.user_data.get("combo_picks", [])
        sel = context.user_data.get("combo_sel", [])
        partes = ["🎰 *ARMAR COMBO* _(máx. {} picks)_\n".format(MAX_COMBO_SIZE),
                  "Selecciona los picks que quieres combinar:\n"]
        for i, pk in enumerate(todos[:10]):
            ch = "✅" if i in sel else "⬜"
            partes.append("{} {}. *{}* - {} @ {}".format(
                ch, i + 1, pk["evento"], pk.get("opcion", ""), pk["cuota"]
            ))
        bots = []
        row = []
        for i in range(min(10, len(todos))):
            ch = "✅" if i in sel else ""
            row.append(InlineKeyboardButton("{}{}".format(ch, i + 1),
                                            callback_data="combo:toggle:{}".format(i)))
            if len(row) == 5:
                bots.append(row)
                row = []
        if row:
            bots.append(row)
        if len(sel) >= 2:
            bots.append([InlineKeyboardButton("🎯 Ver combo", callback_data="combo:ver")])
        bots.append([InlineKeyboardButton("◀️ Menú", callback_data="menu")])
        await _reply(update, "\n".join(partes) + DISCLAIMER, InlineKeyboardMarkup(bots))

    @staticmethod
    async def ver_combo(update, context):
        todos = context.user_data.get("combo_picks", [])
        sel = context.user_data.get("combo_sel", [])
        s = _stats(update.effective_user.id)
        br = s["saldo"] if s["bank_configurado"] else 0.0
        if len(sel) < 2:
            await _reply(update, "⚠️ Selecciona al menos 2 picks para el combo.")
            return
        picks_c = [todos[i] for i in sel if i < len(todos)]
        cuota_c = 1.0
        prob_c = 1.0
        for pk in picks_c:
            cuota_c *= pk["cuota"]
            prob_c *= pk["prob_real"]
        cap = picks_service.calcular_capital_recomendado(prob_c, br, cuota_c)
        cap_s = "${:,.2f}".format(cap) if br > 0 else "- (configura /bank)"
        partes = ["🎰 *TU COMBO*\n"]
        for pk in picks_c:
            partes.append("- *{}* - {} @ {}".format(pk["evento"], pk.get("opcion", ""), pk["cuota"]))
        partes += [
            "\n💰 Cuota total: *{:.2f}*".format(cuota_c),
            "📊 Prob. combinada: *{:.1%}*".format(prob_c),
            "💵 Capital recomendado: *{}*".format(cap_s),
            "ℹ️ _La probabilidad combinada asume independencia entre eventos._",
        ]
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Cambiar selección", callback_data="combo:inicio")],
            [InlineKeyboardButton("◀️ Menú", callback_data="menu")],
        ])
        await _reply(update, "\n".join(partes) + DISCLAIMER, kb)

    @staticmethod
    async def iniciar_apuesta(update, context, pick_idx, deporte):
        picks = context.user_data.get("picks_{}".format(deporte), [])
        if pick_idx >= len(picks):
            await _reply(update, "❌ Pick no encontrado.")
            return
        pick = picks[pick_idx]
        context.user_data["pick_pendiente"] = pick
        s = _stats(update.effective_user.id)
        if not s["bank_configurado"]:
            await _reply(update, "⚠️ Primero configura tu bankroll:\n`/bank <monto>`")
            return
        cap = picks_service.calcular_capital_recomendado(
            pick["prob_real"], s["saldo"], pick.get("cuota", 2.0)
        )
        await _reply(
            update,
            "📌 *Registrar apuesta*\n\n{}\n{} @ {}\n\n"
            "Capital sugerido: *${:,.2f}*\n\n"
            "¿Cuánto quieres apostar? Responde con el monto:".format(
                pick["evento"], pick.get("opcion", ""), pick["cuota"], cap
            )
        )
        context.user_data["esperando_apuesta"] = True

    @staticmethod
    async def recibir_monto_apuesta(update, context):
        try:
            monto = float(update.message.text.replace(",", "."))
        except ValueError:
            await update.message.reply_text(
                "❌ Ingresa un número válido, ej: `50`", parse_mode="Markdown"
            )
            return
        pick = context.user_data.get("pick_pendiente")
        if not pick:
            await update.message.reply_text("❌ Error: pick no encontrado.")
            return
        s = _stats(update.effective_user.id)
        if monto > s["saldo"]:
            await update.message.reply_text(
                "❌ Saldo insuficiente. Tu saldo es ${:,.2f}".format(s["saldo"]),
                parse_mode="Markdown"
            )
            return
        _registrar_apuesta(update.effective_user.id, pick, monto)
        await update.message.reply_text(
            "✅ *Apuesta registrada*\n\n{}\n{} @ {}\nMonto: ${:,.2f}\n\n"
            "Cuando termine el partido, ve a /bank para marcar el resultado.{}".format(
                pick["evento"], pick.get("opcion", ""), pick["cuota"], monto, DISCLAIMER
            ),
            parse_mode="Markdown"
        )
        context.user_data.pop("pick_pendiente", None)
        context.user_data.pop("esperando_apuesta", None)

    @staticmethod
    async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        data = query.data

        if data == "menu":
            await query.edit_message_text(
                "Elige una opción:", reply_markup=_menu_principal(), parse_mode="Markdown"
            )
        elif data.startswith("deporte:"):
            await BotHandlers.mostrar_picks_deporte(update, context, data.split(":")[1])
        elif data == "valor":
            await BotHandlers.cmd_valor(update, context)
        elif data == "bank":
            await BotHandlers._show_bank_query(query, update.effective_user.id)
        elif data == "bank:cambiar":
            await query.edit_message_text(
                "💰 Ingresa tu nuevo capital inicial (responde con el monto):",
                parse_mode="Markdown"
            )
            context.user_data["esperando_bank"] = True
        elif data == "rendimiento":
            await BotHandlers.cmd_rendimiento(update, context)
        elif data == "historial":
            await BotHandlers.mostrar_historial(update, context)
        elif data.startswith("res:"):
            parts = data.split(":")
            ganada = parts[1] == "won"
            res = _marcar_resultado(int(parts[2]), update.effective_user.id, ganada)
            if res["ok"]:
                ic = "✅" if ganada else "❌"
                await query.edit_message_text(
                    "{} *Resultado marcado*\n\nGanancia: *${:+.2f}*\nSaldo actual: *${:,.2f}*{}".format(
                        ic, res["ganancia"], res["saldo"], DISCLAIMER
                    ),
                    parse_mode="Markdown"
                )
            else:
                await query.edit_message_text("❌ Error: {}".format(res["msg"]))
        elif data.startswith("apostar:"):
            parts = data.split(":")
            await BotHandlers.iniciar_apuesta(update, context, int(parts[1]), parts[2])
        elif data == "combo:inicio":
            await BotHandlers.iniciar_combo(update, context)
        elif data.startswith("combo:toggle:"):
            idx = int(data.split(":")[2])
            sel = context.user_data.get("combo_sel", [])
            if idx in sel:
                sel.remove(idx)
            elif len(sel) < MAX_COMBO_SIZE:
                sel.append(idx)
            context.user_data["combo_sel"] = sel
            await BotHandlers._show_combo_selector(update, context)
        elif data == "combo:ver":
            await BotHandlers.ver_combo(update, context)

    @staticmethod
    async def mensaje_texto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if context.user_data.get("esperando_bank"):
            try:
                monto = float(update.message.text.replace(",", "."))
                u = _set_bankroll(update.effective_user.id, monto)
                await update.message.reply_text(
                    "✅ *Bankroll actualizado:* ${:,.2f}{}".format(u.saldo, DISCLAIMER),
                    parse_mode="Markdown"
                )
            except ValueError:
                await update.message.reply_text(
                    "❌ Número inválido. Ej: `1000`", parse_mode="Markdown"
                )
            context.user_data.pop("esperando_bank", None)
        elif context.user_data.get("esperando_apuesta"):
            await BotHandlers.recibir_monto_apuesta(update, context)


async def alerta_previa_partido(context) -> None:
    try:
        job_data = context.job.data or {}
        chat_id = job_data.get("chat_id")
        pick = job_data.get("pick")
        if not chat_id or not pick:
            return
        texto = (
            "🔔 *ALERTA - Partido en 30 minutos*\n\n"
            "{}\n\n📈 Valor: *+{:.1f}%*{}"
        ).format(_fmt_pick(pick), pick["valor_pct"], DISCLAIMER)
        await context.bot.send_message(
            chat_id=chat_id, text=texto, parse_mode="Markdown"
        )
    except Exception as e:
        logger.error("Error en alerta previa: %s", e)
