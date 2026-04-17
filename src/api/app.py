"""
API REST Flask para Radar Maestro
Endpoints para comunicación bot-dashboard
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear app
app = Flask(__name__)
CORS(app)

# Configuración
app.config['JSON_SORT_KEYS'] = False
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 5000))


# Health check
@app.route('/health', methods=['GET'])
def health():
    """Endpoint de salud"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


# Dashboard endpoints
@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Obtiene estadísticas del dashboard"""
    return jsonify({
        'suscriptores_total': 156,
        'picks_generados_hoy': 12,
        'picks_con_valor': 8,
        'roi_promedio': 15.5,
        'yield_promedio': 2.3,
        'apuestas_hoy': 24,
        'aciertos_hoy': 15,
        'tasa_acierto': 62.5
    })


@app.route('/api/dashboard/suscriptores', methods=['GET'])
def get_suscriptores():
    """Obtiene datos de suscriptores"""
    return jsonify({
        'total': 156,
        'activos': 142,
        'inactivos': 14,
        'por_plan': {
            'gratis': 45,
            'básico': 78,
            'premium': 33
        },
        'fuentes': {
            'telegram_directo': 65,
            'referidos': 52,
            'redes_sociales': 39
        }
    })


@app.route('/api/dashboard/ligas', methods=['GET'])
def get_ligas_preferences():
    """Obtiene preferencias de ligas"""
    return jsonify({
        'futbol': {
            'La Liga': 45,
            'Premier': 52,
            'Serie A': 38,
            'Bundesliga': 21
        },
        'tenis': {
            'ATP': 23,
            'WTA': 18
        },
        'basquet': {
            'NBA': 34,
            'EuroLiga': 12
        }
    })


@app.route('/api/dashboard/algoritmo', methods=['GET'])
def get_algoritmo_performance():
    """Obtiene rendimiento del algoritmo"""
    return jsonify({
        'predicciones_totales': 324,
        'aciertos': 201,
        'fallos': 123,
        'tasa_acierto': 62.0,
        'roi': 18.5,
        'mejora_ultimos_7_dias': 2.3,
        'confianza_promedio': 0.72,
        'picks_con_valor': {
            'detectados': 89,
            'apostados': 67,
            'ganados': 42
        }
    })


@app.route('/api/dashboard/partidos-hoy', methods=['GET'])
def get_partidos_hoy():
    """Obtiene partidos programados para hoy"""
    return jsonify({
        'futbol': [
            {
                'id': 1,
                'liga': 'La Liga',
                'local': 'Real Madrid',
                'visitante': 'Barcelona',
                'hora': '15:00',
                'picks_generados': 3,
                'valor_detectado': True
            },
            {
                'id': 2,
                'liga': 'Premier',
                'local': 'Man City',
                'visitante': 'Liverpool',
                'hora': '16:30',
                'picks_generados': 2,
                'valor_detectado': True
            }
        ],
        'tenis': [
            {
                'id': 3,
                'torneo': 'ATP Masters',
                'jugador1': 'Djokovic',
                'jugador2': 'Alcaraz',
                'hora': '10:00',
                'picks_generados': 2,
                'valor_detectado': False
            }
        ],
        'basquet': []
    })


# Bot endpoints
@app.route('/api/bot/picks', methods=['GET'])
def get_bot_picks():
    """Obtiene picks para enviar por telegram"""
    return jsonify({
        'picks': [
            {
                'id': 1,
                'partido': 'Real Madrid vs Barcelona',
                'mercado': 'Gana Local',
                'cuota': 2.10,
                'valor': '+3.2%',
                'confianza': 'FUERTE',
                'descripcion': 'Valor detectado: prob real 50% vs implicita 47.6%'
            },
            {
                'id': 2,
                'partido': 'Man City vs Liverpool',
                'mercado': 'Ambos anotan',
                'cuota': 1.85,
                'valor': '+1.8%',
                'confianza': 'MEDIA',
                'descripcion': 'Ligero valor detectado'
            }
        ],
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/bot/banco', methods=['GET', 'POST'])
def manage_banco():
    """GET: obtiene banco, POST: actualiza banco"""
    if request.method == 'GET':
        usuario_id = request.args.get('usuario_id')
        return jsonify({
            'usuario_id': usuario_id,
            'saldo': 1150.50,
            'saldo_inicial': 1000.0,
            'ganancia': 150.50,
            'roi': 15.05,
            'apuestas_total': 24,
            'apuestas_ganadas': 15,
            'tasa_acierto': 62.5
        })
    
    elif request.method == 'POST':
        data = request.json
        return jsonify({
            'mensaje': 'Banco actualizado',
            'nuevo_saldo': data.get('saldo', 1000)
        })


@app.route('/api/bot/registrar-apuesta', methods=['POST'])
def registrar_apuesta():
    """Registra una apuesta"""
    data = request.json
    return jsonify({
        'exito': True,
        'mensaje': 'Apuesta registrada',
        'apuesta_id': 123,
        'monto': data.get('monto'),
        'cuota': data.get('cuota'),
        'saldo_actualizado': 1100.0
    })


@app.route('/api/analytics/feedback', methods=['POST'])
def registrar_feedback():
    """Registra feedback del análisis"""
    data = request.json
    return jsonify({
        'exito': True,
        'mensaje': 'Feedback registrado',
        'algoritmo_mejorado': True,
        'precisión_nueva': 62.5
    })


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Error interno: {error}")
    return jsonify({'error': 'Error interno del servidor'}), 500


if __name__ == '__main__':
    logger.info(f"🚀 API iniciando en {API_HOST}:{API_PORT}")
    app.run(host=API_HOST, port=API_PORT, debug=os.getenv('API_DEBUG', False))

