"""
Funciones auxiliares y utilidades
"""

from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def formatear_moneda(monto: float, moneda: str = '$') -> str:
    """Formatea un monto como moneda"""
    return f"{moneda}{monto:,.2f}"


def formatear_porcentaje(valor: float, decimales: int = 1) -> str:
    """Formatea un valor como porcentaje"""
    if valor > 0:
        return f"+{valor:.{decimales}f}%"
    else:
        return f"{valor:.{decimales}f}%"


def calcular_roi(saldo_actual: float, saldo_inicial: float) -> float:
    """Calcula ROI"""
    if saldo_inicial == 0:
        return 0
    return ((saldo_actual - saldo_inicial) / saldo_inicial) * 100


def calcular_yield(ganancia: float, total_apostado: float) -> float:
    """Calcula yield"""
    if total_apostado == 0:
        return 0
    return (ganancia / total_apostado) * 100


def es_valor(prob_real: float, cuota: float) -> bool:
    """Detecta si hay valor en una cuota"""
    prob_implicita = 1 / cuota if cuota > 0 else 0
    return prob_real > prob_implicita


def calcular_ev(prob_real: float, cuota: float) -> float:
    """Calcula expected value"""
    return (prob_real * cuota) - 1


def obtener_timestamp() -> str:
    """Obtiene timestamp actual formateado"""
    return datetime.now().isoformat()


def obtener_fecha_formateada(fecha: datetime = None) -> str:
    """Formatea una fecha"""
    if fecha is None:
        fecha = datetime.now()
    return fecha.strftime('%d/%m/%Y %H:%M:%S')


class Logger:
    """Wrapper para logging"""
    
    @staticmethod
    def info(mensaje: str, modulo: str = 'Radar'):
        logger.info(f"[{modulo}] {mensaje}")
    
    @staticmethod
    def error(mensaje: str, modulo: str = 'Radar'):
        logger.error(f"[{modulo}] {mensaje}")
    
    @staticmethod
    def warning(mensaje: str, modulo: str = 'Radar'):
        logger.warning(f"[{modulo}] {mensaje}")
    
    @staticmethod
    def debug(mensaje: str, modulo: str = 'Radar'):
        logger.debug(f"[{modulo}] {mensaje}")

