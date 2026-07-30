#!/bin/bash
# run_frontend.sh - NURU Next.js + React + Tailwind CSS Frontend

echo "========================================"
echo "🚀 LANCEMENT DE NURU - FRONTEND (NEXT.JS)"
echo "========================================"

cd "$(dirname "$0")/frontend" || exit 1

# Charger NVM si disponible
export NVM_DIR="$HOME/.nvm"
export PATH="$HOME/.nvm/versions/node/v24.18.0/bin:$PATH"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

PORT="${PORT:-3000}" API_URL="${API_URL:-http://localhost:8080}" npm run dev -- -p "$PORT"
