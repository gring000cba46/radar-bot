"""
Extractor de cuotas deportivas
Obtiene cuotas de múltiples fuentes
"""

import requests
import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ExtractorCuotas:
    """Extrae cuotas de casas de apuestas"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.cuotas_cache = {}
        self.ultima_actualizacion = None
    
    def obtener_cuotas_futbol(self, liga: str) -> List[Dict]:
        """Obtiene cuotas de fútbol (1X2)"""
        return [
            {
                'id': 'partido_1',
                'deporte': 'Fútbol',
                'liga': liga,
                'local': 'Equipo A',
                'visitante': 'Equipo B',
                'fecha': '2026-04-18',
                'hora': '15:00',
                'mercados': {
                    '1': 2.10,  # Gana Local
                    'X': 3.50,  # Empate
                    '2': 3.20   # Gana Visitante
                }
            }
        ]
    
    def obtener_cuotas_tenis(self, torneo: str) -> List[Dict]:
        """Obtiene cuotas de tenis"""
        return [
            {
                'id': 'partido_tenis_1',
                'deporte': 'Tenis',
                'torneo': torneo,
                'jugador1': 'Jugador A',
                'jugador2': 'Jugador B',
                'fecha': '2026-04-18',
                'hora': '10:00',
                'mercados': {
                    'jugador1': 1.85,
                    'jugador2': 2.05,
                    'over_sets_2.5': 1.95
                }
            }
        ]
    
    def obtener_cuotas_basquet(self, liga: str) -> List[Dict]:
        """Obtiene cuotas de basquetbol"""
        return [
            {
                'id': 'partido_basquet_1',
                'deporte': 'Basquetbol',
                'liga': liga,
                'local': 'Equipo A',
                'visitante': 'Equipo B',
                'fecha': '2026-04-18',
                'hora': '20:00',
                'mercados': {
                    'local': 1.95,
                    'visitante': 1.95,
                    'handicap_-5.5': 1.90
                }
            }
        ]
    
    def obtener_todos_partidos(self) -> Dict:
        """Obtiene todos los partidos disponibles"""
        return {
            'futbol': {
                'La Liga': self.obtener_cuotas_futbol('La Liga'),
                'Premier': self.obtener_cuotas_futbol('Premier League'),
                'Serie A': self.obtener_cuotas_futbol('Serie A')
            },
            'tenis': {
                'ATP': self.obtener_cuotas_tenis('ATP Masters'),
                'WTA': self.obtener_cuotas_tenis('WTA 1000')
            },
            'basquet': {
                'NBA': self.obtener_cuotas_basquet('NBA'),
                'EuroLiga': self.obtener_cuotas_basquet('EuroLiga')
            }
        }
    
    def procesar_cuotas(self, cuotas_raw: Dict) -> Dict:
        """Procesa y estructura cuotas"""
        processed = {}
        for deporte, ligas in cuotas_raw.items():
            processed[deporte] = {}
            for liga, partidos in ligas.items():
                processed[deporte][liga] = [
                    {
                        **partido,
                        'timestamp': datetime.now().isoformat()
                    }
                    for partido in partidos
                ]
        return processed
    
    def detectar_cambios_cuotas(self, cuotas_nuevas: Dict) -> Dict:
        """Detecta cambios en cuotas respecto a cache"""
        cambios = {}
        
        # Comparar con cache anterior
        for deporte in cuotas_nuevas:
            for liga in cuotas_nuevas.get(deporte, {}):
                for partido in cuotas_nuevas[deporte][liga]:
                    partido_id = partido['id']
                    if partido_id in self.cuotas_cache:
                        cambios[partido_id] = {
                            'anterior': self.cuotas_cache[partido_id],
                            'nueva': partido['mercados']
                        }
        
        # Actualizar cache
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

