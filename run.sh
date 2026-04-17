#!/bin/bash

echo "🚀 Iniciando Radar Maestro..."
echo ""

# Activar entorno virtual
source venv/bin/activate

# Crear directorios si no existen
mkdir -p data logs

# Verificar .env
if [ ! -f .env ]; then
    echo "❌ ERROR: Archivo .env no encontrado"
    echo "Copia .env.example a .env y configura tus datos"
    exit 1
fi

# Iniciar bot y API en paralelo
echo "🤖 Iniciando Bot de Telegram..."
python3 src/bot/main.py &
BOT_PID=$!

echo "🌐 Iniciando API Flask..."
python3 src/api/app.py &
API_PID=$!

echo ""
echo "✅ Sistema iniciado!"
echo "  Bot PID: $BOT_PID"
echo "  API PID: $API_PID"
echo ""
echo "Presiona Ctrl+C para detener"
echo ""

# Esperar a que los procesos terminen
wait

