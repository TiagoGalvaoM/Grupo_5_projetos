#!/bin/bash

# Script para iniciar o frontend do NexoClima

echo "🚀 Iniciando Frontend NexoClima..."
echo ""

cd "$(dirname "$0")/frontend"

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências..."
    npm install
fi

# Iniciar servidor de desenvolvimento
echo ""
echo "✅ Iniciando servidor Vite..."
echo "📍 Dashboard: http://localhost:5173"
echo ""

npm run dev
