#!/bin/bash

echo "🚀 Instalando Radar Maestro..."
echo ""

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# Crear directorios
echo "📁 Creando directorios..."
mkdir -p data logs

# Inicializar base de datos
echo "🗄️ Inicializando base de datos..."
python3 -c "from src.models.database import init_db; init_db()"

# Crear archivo .env
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    cp .env.example .env
    echo "⚠️ IMPORTANTE: Edita .env con tus datos de Telegram"
fi

echo ""
echo "✅ Instalación completa!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Edita .env con tus credenciales de Telegram"
echo "2. Ejecuta: python src/bot/main.py (Terminal 1)"
echo "3. Ejecuta: python src/api/app.py (Terminal 2)"
echo ""

