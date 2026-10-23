#!/bin/bash

# Script para executar o pipeline manualmente

echo "🔄 Executando Pipeline NexoClima..."
echo ""

cd "$(dirname "$0")/backend"

# Verificar se .env existe
if [ ! -f ../.env ]; then
    echo "❌ Arquivo .env não encontrado!"
    exit 1
fi

echo "📡 Coletando dados da API Open-Meteo..."
echo "💾 Armazenando RAW no MongoDB..."
echo "🔄 Transformando dados..."
echo "✅ Persistindo no PostgreSQL..."
echo ""

poetry run python scripts/run_pipeline_manual.py

echo ""
echo "✅ Pipeline executado com sucesso!"
echo ""
echo "Verifique os dados em:"
echo "   - MongoDB Atlas (RAW)"
echo "   - Neon PostgreSQL (CURATED)"
echo "   - Dashboard: http://localhost:5173"
