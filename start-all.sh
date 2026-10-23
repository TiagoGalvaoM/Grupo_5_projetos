#!/bin/bash

# Script para iniciar backend e frontend simultaneamente

echo "🚀 Iniciando NexoClima completo..."
echo ""

# Diretório do projeto
PROJECT_DIR="$(dirname "$0")"

# Verificar se .env existe
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "❌ Arquivo .env não encontrado!"
    echo ""
    echo "Execute os seguintes passos:"
    echo "1. cp .env.example .env"
    echo "2. Edite .env com suas credenciais MongoDB Atlas e Neon"
    echo "3. Execute este script novamente"
    exit 1
fi

echo "📋 Este script vai abrir 2 terminais:"
echo "   1. Backend (FastAPI) - http://localhost:8000"
echo "   2. Frontend (React) - http://localhost:5173"
echo ""
echo "Pressione ENTER para continuar..."
read

# Abrir terminal para backend
osascript <<EOF
tell application "Terminal"
    do script "cd '$PROJECT_DIR' && ./start-backend.sh"
    activate
end tell
EOF

# Aguardar 3 segundos
sleep 3

# Abrir terminal para frontend
osascript <<EOF
tell application "Terminal"
    do script "cd '$PROJECT_DIR' && ./start-frontend.sh"
    activate
end tell
EOF

echo ""
echo "✅ Terminais abertos!"
echo ""
echo "Aguarde alguns segundos e acesse:"
echo "   - Backend: http://localhost:8000/docs"
echo "   - Dashboard: http://localhost:5173"
echo ""
