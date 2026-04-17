"""
Algoritmo de análisis de valor en cuotas
"""

import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class AnalizadorCuotas:
    """Analizador inteligente de cuotas deportivas"""
    
    def __init__(self, confianza_minima: float = 0.60):
        """
        Inicializa el analizador
        
        Args:
            confianza_minima: Confianza mínima para generar picks (0-1)
        """
        self.confianza_minima = confianza_minima
    
    def calcular_probabilidad_implicita(self, cuota: float) -> float:
        """
        Calcula la probabilidad implícita de una cuota
        
        Args:
            cuota: Cuota decimal (ej: 2.10)
        
        Returns:
            Probabilidad implícita (0-1)
        """
        if cuota <= 0:
            return 0
        return 1 / cuota
    
    def detectar_valor(self, cuota: float, prob_real: float) -> Dict:
        """
        Detecta si hay valor en una cuota
        
        Args:
            cuota: Cuota decimal
            prob_real: Probabilidad real del evento (0-1)
        
        Returns:
            Diccionario con análisis de valor
        """
        prob_implicita = self.calcular_probabilidad_implicita(cuota)
        hay_valor = prob_real > prob_implicita
        
        if hay_valor:
            porcentaje_valor = ((prob_real - prob_implicita) / prob_implicita) * 100
            expected_value = (prob_real * cuota) - 1
        else:
            porcentaje_valor = 0
            expected_value = 0
        
        return {
            'hay_valor': hay_valor,
            'prob_real': prob_real,
            'prob_implicita': prob_implicita,
            'porcentaje_valor': porcentaje_valor,
            'expected_value': expected_value,
            'diferencia': prob_real - prob_implicita
        }
    
    def generar_pick(self, partido: str, mercado: str, cuota: float, 
                     prob_real: float, confianza: float) -> Dict or None:
        """
        Genera un pick si cumple los criterios
        
        Args:
            partido: Nombre del partido
            mercado: Tipo de mercado (Gana Local, Gana Visitante, etc)
            cuota: Cuota decimal
            prob_real: Probabilidad real
            confianza: Nivel de confianza (0-1)
        
        Returns:
            Pick generado o None si no cumple criterios
        """
        analisis = self.detectar_valor(cuota, prob_real)
        
        # Validar criterios
        if not analisis['hay_valor']:
            return None
        
        if confianza < self.confianza_minima:
            return None
        
        # Clasificar valor
        if analisis['porcentaje_valor'] >= 5:
            nivel_valor = 'FUERTE'
        elif analisis['porcentaje_valor'] >= 2:
            nivel_valor = 'MODERADO'
        else:
            nivel_valor = 'LEVE'
        
        return {
            'partido': partido,
            'mercado': mercado,
            'cuota': cuota,
            'probabilidad_real': prob_real,
            'probabilidad_implicita': analisis['prob_implicita'],
            'valor': f"+{analisis['porcentaje_valor']:.1f}%",
            'nivel_valor': nivel_valor,
            'confianza': confianza,
            'expected_value': analisis['expected_value'],
            'recomendacion': self._generar_recomendacion(analisis)
        }
    
    def _generar_recomendacion(self, analisis: Dict) -> str:
        """Genera recomendación basada en análisis"""
        ev = analisis['expected_value']
        
        if ev >= 0.20:
            return "🟢 JUGAR - Valor muy fuerte"
        elif ev >= 0.10:
            return "🟡 JUGAR - Valor moderado"
        elif ev >= 0.05:
            return "🟡 CONSIDERAR - Valor leve"
        else:
            return "🔴 EVITAR - Sin valor"


class GestorBankroll:
    """Gestor inteligente de bankroll"""
    
    def __init__(self, saldo_inicial: float):
        """
        Inicializa el gestor
        
        Args:
            saldo_inicial: Saldo inicial en moneda
        """
        self.saldo_inicial = saldo_inicial
        self.saldo = saldo_inicial
        self.apuestas = []
        self.total_apostado = 0
        self.total_ganado = 0
    
    def realizar_apuesta(self, monto: float, cuota: float, 
                        ganada: bool) -> Dict:
        """
        Registra una apuesta
        
        Args:
            monto: Monto apostado
            cuota: Cuota de la apuesta
            ganada: Si la apuesta fue ganada
        
        Returns:
            Resultado de la apuesta
        """
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        
        if cuota <= 1:
            raise ValueError("La cuota debe ser mayor a 1")
        
        if ganada:
            ganancia = monto * (cuota - 1)
            self.saldo += ganancia
            self.total_ganado += ganancia
        else:
            ganancia = -monto
            self.saldo += ganancia
        
        self.apuestas.append({
            'monto': monto,
            'cuota': cuota,
            'ganada': ganada,
            'ganancia': ganancia
        })
        
        self.total_apostado += monto
        
        return {
            'ganancia': ganancia,
            'saldo': self.saldo,
            'resultado': 'GANADA' if ganada else 'PERDIDA'
        }
    
    def calcular_roi(self) -> float:
        """
        Calcula el ROI (Return on Investment)
        
        Returns:
            ROI en porcentaje
        """
        if self.saldo_inicial == 0:
            return 0
        
        ganancia = self.saldo - self.saldo_inicial
        return (ganancia / self.saldo_inicial) * 100
    
    def calcular_yield(self) -> float:
        """
        Calcula el yield
        
        Returns:
            Yield en porcentaje
        """
        if self.total_apostado == 0:
            return 0
        
        ganancia = self.saldo - self.saldo_inicial
        return (ganancia / self.total_apostado) * 100
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas del bankroll"""
        total_apuestas = len(self.apuestas)
        aciertos = sum(1 for a in self.apuestas if a['ganada'])
        fallos = total_apuestas - aciertos
        
        tasa_acierto = (aciertos / total_apuestas * 100) if total_apuestas > 0 else 0
        
        return {
            'saldo': self.saldo,
            'saldo_inicial': self.saldo_inicial,
            'ganancia': self.saldo - self.saldo_inicial,
            'roi': self.calcular_roi(),
            'yield': self.calcular_yield(),
            'apuestas': total_apuestas,
            'aciertos': aciertos,
            'fallos': fallos,
            'tasa_acierto': tasa_acierto,
            'total_apostado': self.total_apostado,
            'total_ganado': self.total_ganado
        }

