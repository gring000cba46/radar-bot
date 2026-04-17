#!/bin/bash

echo "🚀 Instalador de Radar Maestro"
echo "================================"
echo ""

# Verificar Python
echo "�� Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    exit 1
fi
echo "✅ Python 3 encontrado"
echo ""

# Crear entorno virtual
echo "✓ Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate
echo "✅ Entorno virtual activado"
echo ""

# Actualizar pip
echo "✓ Actualizando pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✅ pip actualizado"
echo ""

# Instalar dependencias
echo "✓ Instalando dependencias..."
pip install -r requirements.txt
echo "✅ Dependencias instaladas"
echo ""

# Crear directorios
echo "✓ Creando directorios..."
mkdir -p data
mkdir -p logs
mkdir -p src/bot
mkdir -p src/api
mkdir -p src/core
mkdir -p src/models
mkdir -p src/utils
mkdir -p src/dashboard/templates
mkdir -p src/dashboard/static/css
mkdir -p src/dashboard/static/js
echo "✅ Directorios creados"
echo ""

# Copiar archivo .env
if [ ! -f .env ]; then
    echo "✓ Creando .env..."
    cp .env.example .env
    echo "⚠️  Por favor edita .env con tu TELEGRAM_TOKEN"
    echo ""
fi

# Inicializar base de datos
echo "✓ Inicializando base de datos..."
python3 -c "from src.models.database import init_db; init_db()"
echo "✅ Base de datos lista"
echo ""

echo "✅ ¡Instalación completada!"
echo ""
echo "Próximos pasos:"
echo "1. Edita .env: nano .env"
echo "2. Inicia el bot: python3 src/bot/main.py"
echo "3. En otra terminal, inicia el API: python3 src/api/app.py"
echo ""

