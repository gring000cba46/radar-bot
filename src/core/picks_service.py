"""
Servicio de picks: obtiene eventos, aplica algoritmo y devuelve picks listos.
"""

import logging
from typing import Dict, List

from src.core.algoritmo import algoritmo_picks
from src.core.cuotas_extractor import extractor

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Adaptador: convierte formato del extractor → formato algoritmo
# ─────────────────────────────────────────────────────────────

def _adaptar_evento_futbol(partido: Dict, liga: str) -> Dict:
    """Convierte un partido de fútbol del extractor al formato del algoritmo"""
    mercados_raw = partido.get('mercados', {})
    mercados = []

    if '1' in mercados_raw:
        mercados.append({'tipo': '1x2', 'opcion': 'Home', 'cuota': mercados_raw['1']})
    if 'X' in mercados_raw:
        mercados.append({'tipo': '1x2', 'opcion': 'Draw', 'cuota': mercados_raw['X']})
    if '2' in mercados_raw:
        mercados.append({'tipo': '1x2', 'opcion': 'Away', 'cuota': mercados_raw['2']})

    return {
        'deporte': 'Fútbol',
        'liga': liga,
        'local': partido.get('local', 'Local'),
        'visitante': partido.get('visitante', 'Visitante'),
        'hora': partido.get('hora', ''),
        'mercados': mercados,
    }


def _adaptar_evento_tenis(partido: Dict, torneo: str) -> Dict:
    mercados_raw = partido.get('mercados', {})
    j1 = partido.get('jugador1', 'Jugador 1')
    j2 = partido.get('jugador2', 'Jugador 2')
    mercados = []

    if 'jugador1' in mercados_raw:
        mercados.append({'tipo': 'ganador', 'opcion': j1, 'cuota': mercados_raw['jugador1']})
    if 'jugador2' in mercados_raw:
        mercados.append({'tipo': 'ganador', 'opcion': j2, 'cuota': mercados_raw['jugador2']})

    return {
        'deporte': 'Tenis',
        'liga': torneo,
        'local': j1,
        'visitante': j2,
        'hora': partido.get('hora', ''),
        'mercados': mercados,
    }


def _adaptar_evento_basquet(partido: Dict, liga: str) -> Dict:
    mercados_raw = partido.get('mercados', {})
    mercados = []

    if 'local' in mercados_raw:
        mercados.append({'tipo': 'ganador', 'opcion': partido.get('local', 'Local'),
                         'cuota': mercados_raw['local']})
    if 'visitante' in mercados_raw:
        mercados.append({'tipo': 'ganador', 'opcion': partido.get('visitante', 'Visitante'),
                         'cuota': mercados_raw['visitante']})

    return {
        'deporte': 'Basquetbol',
        'liga': liga,
        'local': partido.get('local', 'Local'),
        'visitante': partido.get('visitante', 'Visitante'),
        'hora': partido.get('hora', ''),
        'mercados': mercados,
    }


# ─────────────────────────────────────────────────────────────
# Servicio principal
# ─────────────────────────────────────────────────────────────

class PicksService:
    """Genera picks usando el extractor de cuotas y el algoritmo de valor"""

    def obtener_todos_picks(self) -> List[Dict]:
        """Retorna TODOS los picks válidos de todos los deportes"""
        picks = []
        picks.extend(self.obtener_picks_deporte('Fútbol'))
        picks.extend(self.obtener_picks_deporte('Tenis'))
        picks.extend(self.obtener_picks_deporte('Basquetbol'))
        return picks

    def obtener_picks_deporte(self, deporte: str) -> List[Dict]:
        """Retorna todos los picks válidos de un deporte, agrupados por hora y liga"""
        try:
            todos = self._get_raw_picks(deporte)
            # Ordenar por hora y luego por liga
            todos.sort(key=lambda p: (p.get('hora', '99:99'), p.get('liga', '')))
            return todos
        except Exception as e:
            logger.error(f"Error obteniendo picks de {deporte}: {e}")
            return []

    def obtener_picks_valor_fuerte(self) -> List[Dict]:
        """Retorna solo los picks con valor > 5%"""
        todos = self.obtener_todos_picks()
        return [p for p in todos if p.get('valor_pct', 0) >= 5.0]

    def _get_raw_picks(self, deporte: str) -> List[Dict]:
        picks = []
        todos_partidos = extractor.obtener_todos_partidos()

        if deporte == 'Fútbol':
            for liga, partidos in todos_partidos.get('futbol', {}).items():
                for partido in partidos:
                    evento = _adaptar_evento_futbol(partido, liga)
                    picks.extend(algoritmo_picks.analizar_evento(evento))

        elif deporte == 'Tenis':
            for torneo, partidos in todos_partidos.get('tenis', {}).items():
                for partido in partidos:
                    evento = _adaptar_evento_tenis(partido, torneo)
                    picks.extend(algoritmo_picks.analizar_evento(evento))

        elif deporte == 'Basquetbol':
            for liga, partidos in todos_partidos.get('basquet', {}).items():
                for partido in partidos:
                    evento = _adaptar_evento_basquet(partido, liga)
                    picks.extend(algoritmo_picks.analizar_evento(evento))

        return picks

    def calcular_capital_recomendado(self, prob_real: float, bankroll: float) -> float:
        """
        Kelly Criterion simplificado: f = p - (1-p)/(cuota-1)
        Usamos un máximo del 5 % del bankroll para protección.
        """
        if bankroll <= 0:
            return 0.0
        porcentaje = min(0.05, prob_real - (1 - prob_real))
        porcentaje = max(0.01, porcentaje)
        return round(bankroll * porcentaje, 2)


# Singleton
picks_service = PicksService()
