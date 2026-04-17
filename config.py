"""
Configuración centralizada de la aplicación
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ===== TELEGRAM =====
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# ===== API =====
API_PORT = int(os.getenv('API_PORT', 5000))
API_DEBUG = os.getenv('API_DEBUG', 'False').lower() == 'true'
API_HOST = os.getenv('API_HOST', '0.0.0.0')

# ===== DATABASE =====
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/radar_bot.db')

# ===== ALGORITHM =====
CONFIANZA_MINIMA = float(os.getenv('CONFIANZA_MINIMA', 0.60))
VALOR_MINIMO = float(os.getenv('VALOR_MINIMO', 1.5))

# ===== BANKROLL =====
SALDO_INICIAL = float(os.getenv('SALDO_INICIAL', 1000.0))
PORCENTAJE_APUESTA = float(os.getenv('PORCENTAJE_APUESTA', 5.0))
APUESTA_MAXIMA = float(os.getenv('APUESTA_MAXIMA', 100.0))

# ===== LOGGING =====
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')

