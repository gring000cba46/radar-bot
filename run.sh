#!/bin/bash

echo "🎯 Iniciando Radar Maestro..."
echo "=============================="
echo ""

# Activar entorno virtual
if [ ! -d "venv" ]; then
    echo "❌ Entorno virtual no existe. Ejecuta: ./install.sh"
    exit 1
fi

source venv/bin/activate

# Crear logs si no existe
mkdir -p logs

# Iniciar en background
echo "🤖 Iniciando Bot..."
python3 src/bot/main.py &
BOT_PID=$!

sleep 2

echo "🌐 Iniciando API..."
python3 src/api/app.py &
API_PID=$!

echo ""
echo "✅ Radar Maestro ejecutándose!"
echo ""
echo "📱 Bot: Busca tu bot en Telegram"
echo "🌐 API: http://localhost:5000/api/health"
echo "📊 Dashboard: http://localhost:5000"
echo ""
echo "Para detener: presiona Ctrl+C"
echo ""

# Esperar a que se ejecuten
wait $BOT_PID $API_PID

