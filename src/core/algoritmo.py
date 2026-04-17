"""
Algoritmo inteligente de análisis de cuotas
Detecta valor donde las casas se equivocan
"""

import math
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class AnalizadorCuotas:
    """Analiza cuotas y detecta valor"""
    
    def __init__(self):
        self.historial_analisis = []
        
    def calcular_probabilidad_implicita(self, cuota: float) -> float:
        """
        Calcula probabilidad implícita en una cuota
        P = 1 / cuota
        """
        if cuota <= 0:
            return 0
        return 1 / cuota
    
    def calcular_probabilidad_real(self, datos_historicos: Dict) -> float:
        """
        Calcula probabilidad real basada en datos históricos
        Usa frecuencia de resultados similares
        """
        if not datos_historicos:
            return 0.5
        
        total = datos_historicos.get('total', 1)
        aciertos = datos_historicos.get('aciertos', 0)
        
        return aciertos / total if total > 0 else 0.5
    
    def detectar_valor(self, cuota: float, prob_real: float) -> Dict:
        """
        Detecta si hay valor en una cuota
        Valor = Probabilidad Real > Probabilidad Implícita
        """
        prob_implicita = self.calcular_probabilidad_implicita(cuota)
        
        diferencia = prob_real - prob_implicita
        porcentaje_valor = (diferencia / prob_implicita * 100) if prob_implicita > 0 else 0
        
        hay_valor = prob_real > prob_implicita
        
        return {
            'hay_valor': hay_valor,
            'prob_real': prob_real,
            'prob_implicita': prob_implicita,
            'diferencia': diferencia,
            'porcentaje_valor': porcentaje_valor,
            'expected_value': (prob_real * cuota) - 1  # EV positivo = valor
        }
    
    def analizar_partido(self, partido: Dict) -> Dict:
        """
        Análisis completo de un partido
        """
        logger.info(f"Analizando: {partido.get('nombre')}")
        
        analisis = {
            'nombre': partido.get('nombre'),
            'mercados': {}
        }
        
        for mercado, cuota in partido.get('cuotas', {}).items():
            datos_hist = partido.get('historial', {}).get(mercado, {})
            analisis_mercado = self.detectar_valor(cuota, 
                                                   self.calcular_probabilidad_real(datos_hist))
            analisis['mercados'][mercado] = analisis_mercado
        
        return analisis
    
    def generar_recomendacion(self, analisis: Dict) -> str:
        """Genera recomendación basada en análisis"""
        mercados_valor = {
            k: v for k, v in analisis['mercados'].items() 
            if v['hay_valor']
        }
        
        if not mercados_valor:
            return "❌ Sin valor detectado"
        
        recomendacion = "✅ OPORTUNIDADES ENCONTRADAS:\n"
        for mercado, datos in mercados_valor.items():
            recomendacion += f"\n🎯 {mercado}\n"
            recomendacion += f"Valor: +{datos['porcentaje_valor']:.1f}%\n"
            recomendacion += f"EV: {datos['expected_value']:.2f}"
        
        return recomendacion


class GestorBankroll:
    """Gestiona el bankroll y apuestas"""
    
    def __init__(self, saldo_inicial: float):
        self.saldo = saldo_inicial
        self.historial = []
        self.bankroll_inicial = saldo_inicial
    
    def realizar_apuesta(self, monto: float, cuota: float, resultado: bool) -> Dict:
        """Registra una apuesta y calcula resultado"""
        if monto > self.saldo:
            return {'error': 'Monto excede bankroll'}
        
        ganancia = (monto * cuota - monto) if resultado else -monto
        self.saldo += ganancia
        
        movimiento = {
            'monto': monto,
            'cuota': cuota,
            'resultado': resultado,
            'ganancia': ganancia,
            'saldo_despues': self.saldo
        }
        
        self.historial.append(movimiento)
        return movimiento
    
    def calcular_roi(self) -> float:
        """Calcula ROI total"""
        ganancia_total = self.saldo - self.bankroll_inicial
        return (ganancia_total / self.bankroll_inicial * 100) if self.bankroll_inicial > 0 else 0
    
    def calcular_yield(self, apuestas_totales: float) -> float:
        """Calcula yield (ganancia / total apostado)"""
        ganancia = self.saldo - self.bankroll_inicial
        return (ganancia / apuestas_totales * 100) if apuestas_totales > 0 else 0
    
    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas del bankroll"""
        if not self.historial:
            return {
                'saldo_actual': self.saldo,
                'saldo_inicial': self.bankroll_inicial,
                'ganancia_total': 0,
                'roi': 0,
                'apuestas': 0,
                'aciertos': 0,
                'tasa_acierto': 0
            }
        
        aciertos = sum(1 for a in self.historial if a['resultado'])
        apuestas_totales = len(self.historial)
        
        return {
            'saldo_actual': self.saldo,
            'saldo_inicial': self.bankroll_inicial,
            'ganancia_total': self.saldo - self.bankroll_inicial,
            'roi': self.calcular_roi(),
            'apuestas': apuestas_totales,
            'aciertos': aciertos,
            'tasa_acierto': (aciertos / apuestas_totales * 100) if apuestas_totales > 0 else 0
        }


# Singleton instance
analizador = AnalizadorCuotas()

