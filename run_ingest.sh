#!/bin/bash
# run_ingest.sh

echo "========================================"
echo "📦 LANCEMENT DU PIPELINE D'INGESTION"
echo "========================================"

# Vérifier les dossiers
mkdir -p data/raw data/processed data/ingestion_logs

# Vérifier les fichiers
PDF_COUNT=$(find data/raw -name "*.pdf" | wc -l)
if [ $PDF_COUNT -eq 0 ]; then
    echo "⚠️ Aucun PDF trouvé dans data/raw/"
    echo "   Placez vos fichiers PDF dans ce dossier"
    exit 1
fi

echo "📁 $PDF_COUNT fichiers PDF trouvés"

# Exécuter le pipeline
python -m scripts.ingest_pipeline "$@"

echo ""
echo "✅ Pipeline terminé !"