# scripts/init_env.sh
#!/bin/bash

echo "========================================"
echo "🔧 INITIALISATION DE L'ENVIRONNEMENT"
echo "========================================"

# Créer le fichier .env depuis l'exemple maintenu à la racine
if [ ! -f ".env" ]; then
    echo "📝 Création du fichier .env..."
    cp .env.example .env
    echo "✅ Fichier .env créé"
else
    echo "ℹ️ Fichier .env existe déjà"
fi

# Ajouter au .gitignore
if ! grep -qxF ".env" .gitignore 2>/dev/null; then
    echo ".env" >> .gitignore
    echo "✅ .env ajouté au .gitignore"
fi

echo ""
echo "========================================"
echo "📌 Prochaines étapes:"
echo "1. Modifier le fichier .env avec vos valeurs"
echo "2. Exécuter: python scripts/check_env.py"
echo "========================================"
