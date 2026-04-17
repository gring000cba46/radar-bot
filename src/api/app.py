"""
API REST Flask para Radar Maestro
"""

from flask import Flask, jsonify, request
import logging
from datetime import datetime
import os
import sys

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ===== HEALTH CHECK =====
@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }), 200


# ===== DASHBOARD STATS =====
@app.route('/api/dashboard/stats', methods=['GET'])
def dashboard_stats():
    """Obtiene estadísticas del dashboard"""
    return jsonify({
        "suscriptores_total": 156,
        "picks_generados_hoy": 12,
        "picks_con_valor": 8,
        "roi_promedio": 15.5,
        "yield_promedio": 2.3,
        "apuestas_hoy": 24,
        "aciertos_hoy": 15,
        "tasa_acierto": 62.5,
        "timestamp": datetime.now().isoformat()
    }), 200


# ===== BOT PICKS =====
@app.route('/api/bot/picks', methods=['GET'])
def bot_picks():
    """Obtiene picks para enviar por Telegram"""
    return jsonify({
        "picks": [
            {
                "id": 1,
                "partido": "Real Madrid vs Barcelona",
                "mercado": "Gana Local",
                "cuota": 2.10,
                "valor": "+3.2%",
                "confianza": "FUERTE",
                "probabilidad_real": 0.50,
                "probabilidad_implicita": 0.476,
                "expected_value": 0.21
            },
            {
                "id": 2,
                "partido": "Liverpool vs Manchester City",
                "mercado": "Gana Visitante",
                "cuota": 2.45,
                "valor": "+1.5%",
                "confianza": "MODERADA",
                "probabilidad_real": 0.42,
                "probabilidad_implicita": 0.408,
                "expected_value": 0.018
            }
        ],
        "timestamp": datetime.now().isoformat()
    }), 200


# ===== BANCO =====
@app.route('/api/bot/banco', methods=['GET'])
def get_banco():
    """Obtiene información del bankroll"""
    usuario_id = request.args.get('usuario_id', default=1, type=int)
    
    return jsonify({
        "usuario_id": usuario_id,
        "saldo": 1150.50,
        "saldo_inicial": 1000.0,
        "ganancia": 150.50,
        "roi": 15.05,
        "apuestas_total": 24,
        "apuestas_ganadas": 15,
        "tasa_acierto": 62.5,
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/bot/banco', methods=['POST'])
def update_banco():
    """Actualiza el bankroll"""
    data = request.get_json()
    
    if not data or 'usuario_id' not in data:
        return jsonify({"error": "usuario_id requerido"}), 400
    
    return jsonify({
        "mensaje": "Banco actualizado",
        "nuevo_saldo": data.get('saldo', 1150.50),
        "timestamp": datetime.now().isoformat()
    }), 200


# ===== REGISTRAR APUESTA =====
@app.route('/api/bot/registrar-apuesta', methods=['POST'])
def registrar_apuesta():
    """Registra una nueva apuesta"""
    data = request.get_json()
    
    # Validar datos
    required_fields = ['usuario_id', 'monto', 'cuota']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Campos requeridos faltantes"}), 400
    
    return jsonify({
        "exito": True,
        "mensaje": "Apuesta registrada",
        "apuesta_id": 123,
        "monto": data['monto'],
        "cuota": data['cuota'],
        "saldo_actualizado": 1100.50,
        "timestamp": datetime.now().isoformat()
    }), 201


# ===== DASHBOARD SUSCRIPTORES =====
@app.route('/api/dashboard/suscriptores', methods=['GET'])
def dashboard_suscriptores():
    """Obtiene información de suscriptores"""
    return jsonify({
        "total": 156,
        "activos": 142,
        "inactivos": 14,
        "por_plan": {
            "gratis": 45,
            "basico": 78,
            "premium": 33
        },
        "timestamp": datetime.now().isoformat()
    }), 200


# ===== DASHBOARD LIGAS =====
@app.route('/api/dashboard/ligas', methods=['GET'])
def dashboard_ligas():
    """Obtiene preferencias de ligas"""
    return jsonify({
        "futbol": {
            "La Liga": 45,
            "Premier": 52,
            "Serie A": 38,
            "Bundesliga": 21
        },
        "tenis": {
            "ATP": 23,
            "WTA": 18
        },
        "basquet": {
            "NBA": 34,
            "EuroLiga": 12
        },
        "timestamp": datetime.now().isoformat()
    }), 200


# ===== ALGORITMO PERFORMANCE =====
@app.route('/api/dashboard/algoritmo', methods=['GET'])
def dashboard_algoritmo():
    """Obtiene rendimiento del algoritmo"""
    return jsonify({
        "predicciones_totales": 324,
        "aciertos": 201,
        "fallos": 123,
        "tasa_acierto": 62.0,
        "roi": 18.5,
        "mejora_ultimos_7_dias": 2.3,
        "confianza_promedio": 0.72,
        "picks_con_valor": {
            "detectados": 89,
            "apostados": 67,
            "ganados": 42
        },
        "timestamp": datetime.now().isoformat()
    }), 200


# ===== ERROR HANDLERS =====
@app.errorhandler(404)
def not_found(error):
    """Endpoint no encontrado"""
    return jsonify({"error": "Endpoint no encontrado"}), 404


@app.errorhandler(500)
def server_error(error):
    """Error interno del servidor"""
    logger.error(f"Error en servidor: {error}")
    return jsonify({"error": "Error interno del servidor"}), 500


# ===== MAIN =====
if __name__ == '__main__':
    logger.info("🌐 Iniciando API Radar Maestro...")
    
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('API_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"📡 API ejecutándose en http://localhost:{port}")
    logger.info(f"📚 Documentación: http://localhost:{port}/api/health")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )

