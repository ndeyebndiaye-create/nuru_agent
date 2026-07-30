#!/bin/bash
# run_tests.sh

echo "========================================"
echo "🧪 LANCEMENT DES TESTS NURU"
echo "========================================"

# Suite automatisée maintenue
python -m pytest tests/ -v --tb=short

echo ""
echo "✅ Tests terminés !"
