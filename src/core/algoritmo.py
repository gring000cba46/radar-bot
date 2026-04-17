"""
Algoritmo de análisis de valor en cuotas
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# ALGORITMO MEJORADO – Menos conservador, usa cuota como base
# ─────────────────────────────────────────────────────────────

class AlgoritmoPicks:
    """Analiza eventos y genera picks válidos con valor real"""

    CONFIG_DEPORTES = {
        'Fútbol': {'prob_minima': 0.55, 'cuota_minima': 1.15},
        'Tenis': {'prob_minima': 0.55, 'cuota_minima': 1.15},
        'Basquetbol': {'prob_minima': 0.55, 'cuota_minima': 1.15},
        'Béisbol': {'prob_minima': 0.55, 'cuota_minima': 1.15},
        'Hockey': {'prob_minima': 0.55, 'cuota_minima': 1.15},
    }

    def analizar_evento(self, evento: Dict) -> List[Dict]:
        """Analiza un evento y retorna sus picks válidos"""
        try:
            deporte = evento.get('deporte', 'Fútbol')
            config = self.CONFIG_DEPORTES.get(deporte, self.CONFIG_DEPORTES['Fútbol'])

            picks_validos = []
            for mercado in evento.get('mercados', []):
                pick = self._analizar_mercado(evento, mercado, deporte, config)
                if pick and pick['pick_valido']:
                    picks_validos.append(pick)

            if picks_validos:
                return [max(picks_validos, key=lambda x: x['valor_pct'])]
            return []

        except Exception as e:
            logger.error(f"Error analizando evento: {e}")
            return []

    def analizar_evento_todos(self, evento: Dict) -> List[Dict]:
        """Retorna TODOS los picks válidos del evento (no solo el mejor)"""
        try:
            deporte = evento.get('deporte', 'Fútbol')
            config = self.CONFIG_DEPORTES.get(deporte, self.CONFIG_DEPORTES['Fútbol'])

            picks_validos = []
            for mercado in evento.get('mercados', []):
                pick = self._analizar_mercado(evento, mercado, deporte, config)
                if pick and pick['pick_valido']:
                    picks_validos.append(pick)
            return picks_validos

        except Exception as e:
            logger.error(f"Error analizando evento (todos): {e}")
            return []

    def _analizar_mercado(self, evento: Dict, mercado: Dict,
                          deporte: str, config: Dict) -> Optional[Dict]:
        try:
            local = evento.get('local', '')
            visitante = evento.get('visitante', evento.get('away_team', ''))
            cuota = mercado.get('cuota', 1.0)
            opcion = mercado.get('opcion', '')
            tipo_mercado = mercado.get('tipo', '')

            if cuota <= 1:
                return None

            prob_implicita = 1 / cuota
            prob_real = self._calcular_prob_real(
                local, opcion, tipo_mercado, deporte, prob_implicita
            )

            valor_pct = ((prob_real - prob_implicita) / prob_implicita) * 100
            ev = (prob_real * cuota) - 1

            prob_minima = config['prob_minima']
            cuota_minima = config['cuota_minima']

            cumple_prob = prob_real >= prob_minima
            cumple_cuota = cuota >= cuota_minima
            cumple_valor = valor_pct >= 1

            pick_valido = cumple_prob and cumple_cuota and cumple_valor

            pick = {
                'evento': f"{local} vs {visitante}",
                'local': local,
                'visitante': visitante,
                'liga': evento.get('liga', ''),
                'deporte': deporte,
                'hora': evento.get('hora', ''),
                'tipo_mercado': tipo_mercado,
                'opcion': opcion,
                'cuota': round(cuota, 2),
                'prob_implicita': round(prob_implicita, 4),
                'prob_real': round(prob_real, 4),
                'valor_pct': round(valor_pct, 2),
                'expected_value': round(ev, 4),
                'confianza': round(prob_real, 2),
                'pick_valido': pick_valido,
                'razon_rechazo': None,
            }

            if not pick_valido:
                razones = []
                if not cumple_prob:
                    razones.append(f"Prob {prob_real:.0%} < {prob_minima:.0%}")
                if not cumple_cuota:
                    razones.append(f"Cuota {cuota:.2f} < {cuota_minima:.2f}")
                if not cumple_valor:
                    razones.append(f"Valor {valor_pct:.2f}%")
                pick['razon_rechazo'] = ' | '.join(razones)

            return pick

        except Exception as e:
            logger.error(f"Error analizando mercado: {e}")
            return None

    def _calcular_prob_real(self, local: str, opcion: str,
                            tipo_mercado: str, deporte: str,
                            prob_implicita: float) -> float:
        if deporte == 'Fútbol':
            return self._calcular_prob_futbol(opcion, tipo_mercado, prob_implicita)
        elif deporte == 'Tenis':
            return self._calcular_prob_tenis(prob_implicita)
        elif deporte == 'Basquetbol':
            return self._calcular_prob_basquet(prob_implicita)
        else:
            return prob_implicita

    def _calcular_prob_futbol(self, opcion: str,
                              tipo_mercado: str,
                              prob_implicita: float) -> float:
        if tipo_mercado == '1x2':
            if opcion == 'Draw':
                if prob_implicita >= 0.25:
                    return min(prob_implicita + 0.08, 0.90)
                return prob_implicita
            elif prob_implicita >= 0.67:
                return min(prob_implicita + 0.05, 0.95)
            elif prob_implicita >= 0.60:
                return min(prob_implicita + 0.04, 0.90)
            elif prob_implicita >= 0.50:
                return min(prob_implicita + 0.03, 0.85)
            else:
                return prob_implicita
        elif tipo_mercado == 'goles':
            if 'Over' in opcion:
                return min(prob_implicita + 0.05, 0.90)
            return prob_implicita
        return prob_implicita

    def _calcular_prob_tenis(self, prob_implicita: float) -> float:
        if prob_implicita >= 0.65:
            return min(prob_implicita + 0.08, 0.95)
        elif prob_implicita >= 0.60:
            return min(prob_implicita + 0.06, 0.90)
        elif prob_implicita >= 0.55:
            return min(prob_implicita + 0.04, 0.85)
        return prob_implicita

    def _calcular_prob_basquet(self, prob_implicita: float) -> float:
        if prob_implicita >= 0.60:
            return min(prob_implicita + 0.05, 0.90)
        return prob_implicita


# Singleton
algoritmo_picks = AlgoritmoPicks()


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

