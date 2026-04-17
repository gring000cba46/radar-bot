"""
Servicio de gestión de combinadas
"""

import json
import logging
from datetime import datetime
from src.models.database import SessionLocal, Combinada, Usuario

logger = logging.getLogger(__name__)


class CombinadaService:

    @staticmethod
    def crear(telegram_id: str, picks_seleccionados: list, monto: float) -> dict:
        """
        Guarda una nueva combinada.

        picks_seleccionados: lista de dicts con datos del pick
        Retorna dict con datos de la combinada creada.
        """
        db = SessionLocal()
        try:
            usuario = db.query(Usuario).filter(
                Usuario.telegram_id == str(telegram_id)
            ).first()

            if not usuario:
                raise ValueError(f"Usuario no encontrado: {telegram_id}")

            cuota_total = 1.0
            prob_total = 1.0
            picks_ids = []
            picks_data = []

            for p in picks_seleccionados:
                cuota_total = round(cuota_total * p['cuota'], 4)
                prob_total = round(prob_total * (p['probabilidad_real'] / 100), 4)
                picks_ids.append(p['id'])
                picks_data.append({
                    'id': p['id'],
                    'partido': p['partido'],
                    'liga': p.get('liga', ''),
                    'mercado': p['mercado'],
                    'cuota': p['cuota'],
                    'probabilidad_real': p['probabilidad_real'],
                })

            combinada = Combinada(
                usuario_id=usuario.id,
                picks_ids=json.dumps(picks_ids),
                picks_data=json.dumps(picks_data),
                cuota_total=cuota_total,
                prob_total=prob_total,
                monto=monto,
                resultado='PENDIENTE',
            )
            db.add(combinada)
            db.commit()
            db.refresh(combinada)

            result = _snapshot(combinada)
            logger.info(
                f"✅ Combinada {combinada.id} creada para {telegram_id}: "
                f"{len(picks_seleccionados)} picks, cuota {cuota_total:.2f}, monto ${monto}"
            )
            return result
        finally:
            db.close()

    @staticmethod
    def finalizar(combinada_id: int, resultado: str, telegram_id: str) -> None:
        """Marca una combinada como GANADA o PERDIDA y actualiza el bank."""
        db = SessionLocal()
        try:
            combinada = db.query(Combinada).filter(Combinada.id == combinada_id).first()
            if not combinada:
                return

            combinada.resultado = resultado
            combinada.finalizado = datetime.utcnow()

            usuario = db.query(Usuario).filter(Usuario.id == combinada.usuario_id).first()

            if resultado == 'GANADA':
                ganancia = round(combinada.monto * (combinada.cuota_total - 1), 2)
                combinada.ganancia = ganancia
                usuario.bank_actual = round(usuario.bank_actual + combinada.monto + ganancia, 2)
                usuario.apuestas_ganadas += 1
            else:
                combinada.ganancia = -combinada.monto

            usuario.apuestas_totales += 1
            usuario.roi = (
                ((usuario.bank_actual - usuario.bank_inicial) / usuario.bank_inicial) * 100
                if usuario.bank_inicial > 0 else 0.0
            )
            usuario.actualizado = datetime.utcnow()
            db.commit()
            logger.info(f"✅ Combinada {combinada_id} finalizada: {resultado}")
        finally:
            db.close()

    @staticmethod
    def obtener_historial(telegram_id: str, limite: int = 10) -> list:
        """Devuelve el historial de combinadas del usuario (más recientes primero)."""
        db = SessionLocal()
        try:
            usuario = db.query(Usuario).filter(
                Usuario.telegram_id == str(telegram_id)
            ).first()
            if not usuario:
                return []

            combinadas = (
                db.query(Combinada)
                .filter(Combinada.usuario_id == usuario.id)
                .order_by(Combinada.creado.desc())
                .limit(limite)
                .all()
            )
            return [_snapshot(c) for c in combinadas]
        finally:
            db.close()


def _snapshot(c: Combinada) -> dict:
    picks_data = []
    try:
        picks_data = json.loads(c.picks_data) if c.picks_data else []
    except Exception:
        pass

    return {
        'id': c.id,
        'picks_data': picks_data,
        'picks_count': len(picks_data),
        'cuota_total': c.cuota_total,
        'prob_total': c.prob_total,
        'monto': c.monto,
        'resultado': c.resultado,
        'ganancia': c.ganancia,
        'creado': c.creado.strftime('%d/%m %H:%M') if c.creado else '',
        'finalizado': c.finalizado.strftime('%d/%m %H:%M') if c.finalizado else None,
    }


combinada_service = CombinadaService()
