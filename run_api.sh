#!/bin/bash
# run_api.sh

echo "========================================"
echo "🚀 LANCEMENT DE L'API NURU"
echo "========================================"

# Vérifier les variables d'environnement
if [ ! -f ".env" ]; then
    echo "⚠️ Fichier .env non trouvé"
    echo "   Créez-le avec vos variables d'environnement"
    exit 1
fi

# Charger les variables d'environnement
set -a
. ./.env
set +a

# Lancer l'API
python -m backend.app.api.main
