"""
Configuración centralizada del proyecto
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ===== TELEGRAM =====
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# ===== DATABASE =====
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/radar_bot.db')

# ===== API =====
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 5000))
API_DEBUG = os.getenv('API_DEBUG', 'False').lower() == 'true'

# ===== ALGORITMO =====
ALGORITMO_CONFIANZA_MIN = float(os.getenv('ALGORITMO_CONFIANZA_MIN', 0.60))
ALGORITMO_VALOR_MIN = float(os.getenv('ALGORITMO_VALOR_MIN', 0.01))

# ===== BANKROLL =====
BANKROLL_INICIAL = float(os.getenv('BANKROLL_INICIAL', 1000))
PORCENTAJE_APUESTA = float(os.getenv('PORCENTAJE_APUESTA', 0.05))

# ===== NOTIFICACIONES =====
NOTIF_PICKS_ACTIVA = os.getenv('NOTIF_PICKS_ACTIVA', 'True').lower() == 'true'
NOTIF_REPORTE_DIARIO = os.getenv('NOTIF_REPORTE_DIARIO', 'True').lower() == 'true'
NOTIF_HORA_REPORTE = os.getenv('NOTIF_HORA_REPORTE', '09:00')

# ===== DEBUG =====
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Validar configuración crítica
if not TELEGRAM_TOKEN:
    print("⚠️ ADVERTENCIA: TELEGRAM_TOKEN no configurado en .env")

if not TELEGRAM_CHAT_ID:
    print("⚠️ ADVERTENCIA: TELEGRAM_CHAT_ID no configurado en .env")

