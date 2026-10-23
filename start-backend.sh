#!/bin/bash

# Script para iniciar o backend do NexoClima

echo "🚀 Iniciando Backend NexoClima..."
echo ""

cd "$(dirname "$0")/backend"

# Verificar se Poetry está instalado
if ! command -v poetry &> /dev/null; then
    echo "⚠️  Poetry não encontrado. Instalando..."
    pip install poetry
fi

# Instalar dependências
echo "📦 Instalando dependências..."
poetry install

# Verificar se .env existe
if [ ! -f ../.env ]; then
    echo "❌ Arquivo .env não encontrado!"
    echo "Execute: cp .env.example .env"
    echo "E configure suas credenciais MongoDB e Neon"
    exit 1
fi

# Criar/atualizar banco de dados
echo "🗄️  Criando/atualizando banco de dados..."
poetry run alembic upgrade head

# Popular dados iniciais (só se necessário)
echo "🌱 Populando dados iniciais..."
poetry run python scripts/seed_initial_data.py 2>/dev/null || echo "Dados já existem, continuando..."

# Iniciar servidor
echo ""
echo "✅ Iniciando servidor FastAPI..."
echo "📍 Backend: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""

poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
