#!/bin/bash
# run_all.sh - Lance API FastAPI + Frontend Next.js

echo "========================================"
echo "🚀 LANCEMENT DE NURU (API + NEXT.JS FRONTEND)"
echo "========================================"

API_PORT=8080
FRONTEND_PORT=3000
mkdir -p logs

# Arrêter les processus existants sur les ports 8080 et 3000
pkill -f "backend.app.api.main" 2>/dev/null || true
pkill -f "next dev" 2>/dev/null || true

# Activer l'environnement Python si disponible
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 1. Lancer l'API FastAPI en arrière-plan
echo "📡 Lancement de l'API FastAPI sur le port $API_PORT..."
python -m backend.app.api.main > logs/api.log 2>&1 &
API_PID=$!

sleep 2

# 2. Lancer le Frontend Next.js en arrière-plan
echo "🎨 Lancement du Frontend Next.js sur le port $FRONTEND_PORT..."
export NVM_DIR="$HOME/.nvm"
export PATH="$HOME/.nvm/versions/node/v24.18.0/bin:$PATH"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

(cd frontend && PORT=$FRONTEND_PORT API_URL=http://localhost:$API_PORT NEXT_PUBLIC_API_URL=http://localhost:$API_PORT npm run dev) > logs/frontend.log 2>&1 &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "✅ NURU est en cours d'exécution !"
echo "========================================"
echo "🎨 Application Web (Frontend) : http://localhost:$FRONTEND_PORT"
echo "📚 Documentation API Backend  : http://localhost:$API_PORT/docs"
echo "========================================"
echo "📝 Logs disponibles :"
echo "   - API Backend : logs/api.log"
echo "   - Frontend    : logs/frontend.log"
echo "========================================"
