"""
Servicio de gestión de usuarios
"""

import logging
from datetime import datetime
from src.models.database import SessionLocal, Usuario

logger = logging.getLogger(__name__)


class UsuarioService:

    @staticmethod
    def obtener_o_crear(telegram_id: str, nombre: str, bank_inicial: float = 1000.0) -> dict:
        """Obtiene un usuario existente o crea uno nuevo."""
        db = SessionLocal()
        try:
            usuario = db.query(Usuario).filter(
                Usuario.telegram_id == str(telegram_id)
            ).first()

            if not usuario:
                try:
                    usuario = Usuario(
                        telegram_id=str(telegram_id),
                        nombre=nombre,
                        bank_inicial=bank_inicial,
                        bank_actual=bank_inicial,
                        roi=0.0,
                        apuestas_totales=0,
                        apuestas_ganadas=0,
                    )
                    db.add(usuario)
                    db.commit()
                    db.refresh(usuario)
                    logger.info(f"✅ Usuario creado: {telegram_id} ({nombre})")
                except Exception:
                    db.rollback()
                    usuario = db.query(Usuario).filter(
                        Usuario.telegram_id == str(telegram_id)
                    ).first()
            else:
                # Actualizar nombre si cambió
                if usuario.nombre != nombre:
                    usuario.nombre = nombre
                    db.commit()

            return _snapshot(usuario)
        finally:
            db.close()

    @staticmethod
    def obtener(telegram_id: str) -> dict | None:
        """Devuelve datos del usuario o None si no existe."""
        db = SessionLocal()
        try:
            usuario = db.query(Usuario).filter(
                Usuario.telegram_id == str(telegram_id)
            ).first()
            return _snapshot(usuario) if usuario else None
        finally:
            db.close()

    @staticmethod
    def actualizar_bank(telegram_id: str, nuevo_bank: float) -> None:
        """Actualiza el bank actual del usuario."""
        db = SessionLocal()
        try:
            usuario = db.query(Usuario).filter(
                Usuario.telegram_id == str(telegram_id)
            ).first()
            if usuario:
                usuario.bank_actual = nuevo_bank
                usuario.roi = (
                    ((nuevo_bank - usuario.bank_inicial) / usuario.bank_inicial) * 100
                    if usuario.bank_inicial > 0 else 0.0
                )
                usuario.actualizado = datetime.utcnow()
                db.commit()
        finally:
            db.close()

    @staticmethod
    def registrar_resultado(telegram_id: str, ganada: bool, ganancia: float) -> None:
        """Actualiza estadísticas después de una combinada resuelta."""
        db = SessionLocal()
        try:
            usuario = db.query(Usuario).filter(
                Usuario.telegram_id == str(telegram_id)
            ).first()
            if usuario:
                usuario.apuestas_totales += 1
                if ganada:
                    usuario.apuestas_ganadas += 1
                    usuario.bank_actual += ganancia
                usuario.roi = (
                    ((usuario.bank_actual - usuario.bank_inicial) / usuario.bank_inicial) * 100
                    if usuario.bank_inicial > 0 else 0.0
                )
                usuario.actualizado = datetime.utcnow()
                db.commit()
        finally:
            db.close()


def _snapshot(u: Usuario) -> dict:
    """Convierte modelo a diccionario plano (evita lazy-load fuera de sesión)."""
    return {
        'id': u.id,
        'telegram_id': u.telegram_id,
        'nombre': u.nombre,
        'bank_inicial': u.bank_inicial,
        'bank_actual': u.bank_actual,
        'roi': u.roi,
        'apuestas_totales': u.apuestas_totales,
        'apuestas_ganadas': u.apuestas_ganadas,
    }


usuario_service = UsuarioService()
