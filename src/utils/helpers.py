"""
Funciones auxiliares para Radar Maestro
"""

from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def formatear_moneda(monto: float, simbolo: str = '$') -> str:
    """
    Formatea un monto a moneda
    
    Args:
        monto: Cantidad a formatear
        simbolo: Símbolo de moneda
    
    Returns:
        String formateado
    """
    return f"{simbolo}{monto:,.2f}"


def formatear_porcentaje(valor: float, decimales: int = 2) -> str:
    """
    Formatea un porcentaje
    
    Args:
        valor: Valor numérico
        decimales: Cantidad de decimales
    
    Returns:
        String con formato de porcentaje
    """
    return f"{valor:.{decimales}f}%"


def calcular_roi(saldo_inicial: float, saldo_actual: float) -> float:
    """
    Calcula el ROI (Return on Investment)
    
    Args:
        saldo_inicial: Saldo inicial
        saldo_actual: Saldo actual
    
    Returns:
        ROI en porcentaje
    """
    if saldo_inicial == 0:
        return 0
    
    ganancia = saldo_actual - saldo_inicial
    return (ganancia / saldo_inicial) * 100


def calcular_yield(ganancia: float, total_apostado: float) -> float:
    """
    Calcula el yield
    
    Args:
        ganancia: Ganancia total
        total_apostado: Total apostado
    
    Returns:
        Yield en porcentaje
    """
    if total_apostado == 0:
        return 0
    
    return (ganancia / total_apostado) * 100


def obtener_emoji_valor(valor: float) -> str:
    """
    Obtiene emoji según el nivel de valor
    
    Args:
        valor: Porcentaje de valor
    
    Returns:
        Emoji correspondiente
    """
    if valor >= 5:
        return "🟢"  # Valor fuerte
    elif valor >= 2:
        return "🟡"  # Valor moderado
    else:
        return "🔵"  # Valor leve


def obtener_emoji_confianza(confianza: float) -> str:
    """
    Obtiene emoji según el nivel de confianza
    
    Args:
        confianza: Confianza (0-1)
    
    Returns:
        Emoji correspondiente
    """
    if confianza >= 0.8:
        return "⭐⭐⭐"
    elif confianza >= 0.6:
        return "⭐⭐"
    else:
        return "⭐"


def formatear_pick(pick: dict) -> str:
    """
    Formatea un pick para mostrar en Telegram
    
    Args:
        pick: Diccionario con datos del pick
    
    Returns:
        String formateado
    """
    return f"""
{obtener_emoji_valor(float(pick['valor'].rstrip('%')))} **{pick['partido']}**
📍 {pick['mercado']}
💰 Cuota: {pick['cuota']}
💎 Valor: {pick['valor']}
📊 EV: {pick['expected_value']:.3f}
⭐ Confianza: {int(pick['confianza']*100)}%
"""


def obtener_fecha_formateada() -> str:
    """
    Obtiene fecha formateada
    
    Returns:
        Fecha en formato DD/MM/YYYY
    """
    return datetime.now().strftime("%d/%m/%Y")


def obtener_hora_formateada() -> str:
    """
    Obtiene hora formateada
    
    Returns:
        Hora en formato HH:MM:SS
    """
    return datetime.now().strftime("%H:%M:%S")

