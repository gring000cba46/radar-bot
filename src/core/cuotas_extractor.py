"""
Extractor de cuotas deportivas
Obtiene cuotas de múltiples fuentes
"""

import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ExtractorCuotas:
    """Extrae cuotas de casas de apuestas (demo con datos variados realistas)"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.cuotas_cache = {}
        self.ultima_actualizacion = None

    def obtener_cuotas_futbol(self, liga: str) -> List[Dict]:
        """Retorna cuotas de fútbol con variedad realista según la liga"""
        data = {
            'La Liga': [
                {
                    'id': 'laliga_1', 'deporte': 'Fútbol', 'liga': liga,
                    'local': 'Barcelona', 'visitante': 'Getafe',
                    'fecha': '2026-04-18', 'hora': '20:00',
                    'mercados': {'1': 1.38, 'X': 4.50, '2': 8.00},
                },
                {
                    'id': 'laliga_2', 'deporte': 'Fútbol', 'liga': liga,
                    'local': 'Real Madrid', 'visitante': 'Celta Vigo',
                    'fecha': '2026-04-18', 'hora': '18:30',
                    'mercados': {'1': 1.45, 'X': 4.20, '2': 7.00},
                },
                {
                    'id': 'laliga_3', 'deporte': 'Fútbol', 'liga': liga,
                    'local': 'Atletico Madrid', 'visitante': 'Sevilla',
                    'fecha': '2026-04-18', 'hora': '22:00',
                    'mercados': {'1': 1.72, 'X': 3.50, '2': 5.00},
                },
            ],
            'Premier League': [
                {
                    'id': 'premier_1', 'deporte': 'Fútbol', 'liga': liga,
                    'local': 'Manchester City', 'visitante': 'Leicester City',
                    'fecha': '2026-04-18', 'hora': '17:30',
                    'mercados': {'1': 1.30, 'X': 5.00, '2': 10.00},
                },
                {
                    'id': 'premier_2', 'deporte': 'Fútbol', 'liga': liga,
                    'local': 'Liverpool', 'visitante': 'Everton',
                    'fecha': '2026-04-18', 'hora': '20:00',
                    'mercados': {'1': 1.50, 'X': 4.00, '2': 6.50},
                },
            ],
            'Serie A': [
                {
                    'id': 'seriea_1', 'deporte': 'Fútbol', 'liga': liga,
                    'local': 'Inter Milan', 'visitante': 'Cagliari',
                    'fecha': '2026-04-18', 'hora': '20:45',
                    'mercados': {'1': 1.22, 'X': 6.00, '2': 12.00},
                },
                {
                    'id': 'seriea_2', 'deporte': 'Fútbol', 'liga': liga,
                    'local': 'RC Lens', 'visitante': 'Toulouse',
                    'fecha': '2026-04-18', 'hora': '19:00',
                    'mercados': {'1': 1.48, 'X': 3.80, '2': 6.50},
                },
            ],
        }
        return data.get(liga, data['La Liga'])

    def obtener_cuotas_tenis(self, torneo: str) -> List[Dict]:
        """Retorna cuotas de tenis con valores variados realistas"""
        data = {
            'ATP Masters': [
                {
                    'id': 'atp_1', 'deporte': 'Tenis', 'torneo': torneo,
                    'jugador1': 'Alexander Zverev', 'jugador2': 'F. Cerundolo',
                    'fecha': '2026-04-18', 'hora': '14:00',
                    'mercados': {'jugador1': 1.41, 'jugador2': 2.90},
                },
                {
                    'id': 'atp_2', 'deporte': 'Tenis', 'torneo': torneo,
                    'jugador1': 'Iga Swiatek', 'jugador2': 'Mirra Andreeva',
                    'fecha': '2026-04-18', 'hora': '16:00',
                    'mercados': {'jugador1': 1.52, 'jugador2': 2.55},
                },
                {
                    'id': 'atp_3', 'deporte': 'Tenis', 'torneo': torneo,
                    'jugador1': 'Carlos Alcaraz', 'jugador2': 'A. Fils',
                    'fecha': '2026-04-18', 'hora': '12:30',
                    'mercados': {'jugador1': 1.35, 'jugador2': 3.20},
                },
            ],
            'WTA 1000': [
                {
                    'id': 'wta_1', 'deporte': 'Tenis', 'torneo': torneo,
                    'jugador1': 'Aryna Sabalenka', 'jugador2': 'Jasmine Paolini',
                    'fecha': '2026-04-18', 'hora': '15:00',
                    'mercados': {'jugador1': 1.48, 'jugador2': 2.65},
                },
                {
                    'id': 'wta_2', 'deporte': 'Tenis', 'torneo': torneo,
                    'jugador1': 'Coco Gauff', 'jugador2': 'Danielle Collins',
                    'fecha': '2026-04-18', 'hora': '18:00',
                    'mercados': {'jugador1': 1.55, 'jugador2': 2.40},
                },
            ],
        }
        return data.get(torneo, data['ATP Masters'])

    def obtener_cuotas_basquet(self, liga: str) -> List[Dict]:
        """Retorna cuotas de basquetbol con valores variados realistas"""
        data = {
            'NBA': [
                {
                    'id': 'nba_1', 'deporte': 'Basquetbol', 'liga': liga,
                    'local': 'Boston Celtics', 'visitante': 'Toronto Raptors',
                    'fecha': '2026-04-18', 'hora': '01:30',
                    'mercados': {'local': 1.35, 'visitante': 3.10},
                },
                {
                    'id': 'nba_2', 'deporte': 'Basquetbol', 'liga': liga,
                    'local': 'Golden State Warriors', 'visitante': 'Dallas Mavericks',
                    'fecha': '2026-04-18', 'hora': '04:00',
                    'mercados': {'local': 1.62, 'visitante': 2.30},
                },
            ],
            'EuroLiga': [
                {
                    'id': 'euro_1', 'deporte': 'Basquetbol', 'liga': liga,
                    'local': 'Real Madrid Basket', 'visitante': 'Olympiacos',
                    'fecha': '2026-04-18', 'hora': '21:00',
                    'mercados': {'local': 1.45, 'visitante': 2.80},
                },
            ],
        }
        return data.get(liga, data['NBA'])

    def obtener_todos_partidos(self) -> Dict:
        """Obtiene todos los partidos disponibles"""
        return {
            'futbol': {
                'La Liga': self.obtener_cuotas_futbol('La Liga'),
                'Premier League': self.obtener_cuotas_futbol('Premier League'),
                'Serie A': self.obtener_cuotas_futbol('Serie A'),
            },
            'tenis': {
                'ATP Masters': self.obtener_cuotas_tenis('ATP Masters'),
                'WTA 1000': self.obtener_cuotas_tenis('WTA 1000'),
            },
            'basquet': {
                'NBA': self.obtener_cuotas_basquet('NBA'),
                'EuroLiga': self.obtener_cuotas_basquet('EuroLiga'),
            },
        }

    def procesar_cuotas(self, cuotas_raw: Dict) -> Dict:
        """Procesa y estructura cuotas"""
        processed = {}
        for deporte, ligas in cuotas_raw.items():
            processed[deporte] = {}
            for liga, partidos in ligas.items():
                processed[deporte][liga] = [
                    {**partido, 'timestamp': datetime.now().isoformat()}
                    for partido in partidos
                ]
        return processed

    def detectar_cambios_cuotas(self, cuotas_nuevas: Dict) -> Dict:
        """Detecta cambios en cuotas respecto a cache"""
        cambios = {}
        for deporte in cuotas_nuevas:
            for liga in cuotas_nuevas.get(deporte, {}):
                for partido in cuotas_nuevas[deporte][liga]:
                    partido_id = partido['id']
                    if partido_id in self.cuotas_cache:
                        cambios[partido_id] = {
                            'anterior': self.cuotas_cache[partido_id],
                            'nueva': partido['mercados'],
                        }
        self.cuotas_cache = {
            p['id']: p['mercados']
            for d in cuotas_nuevas.values()
            for l in d.values()
            for p in l
        }
        self.ultima_actualizacion = datetime.now()
        return cambios


# Singleton instance
extractor = ExtractorCuotas()

