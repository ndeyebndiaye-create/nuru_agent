# scripts/check_env.py
"""
Vérifie que les variables d'environnement sont correctement configurées.
"""
import sys
from pathlib import Path

# Les consoles Windows peuvent encore utiliser CP1252.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ajouter le chemin du projet
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.utils.env_loader import get_env

def check_env():
    """Vérifie les variables d'environnement."""
    
    print("\n" + "=" * 80)
    print("🔍 VÉRIFICATION DES VARIABLES D'ENVIRONNEMENT")
    print("=" * 80)
    
    # Variables à vérifier
    env_vars = [
        ("QDRANT_URL", "URL Qdrant", True, True),
        ("QDRANT_API_KEY", "Clé API Qdrant (optionnelle en local)", False, True),
        ("QDRANT_COLLECTION", "Nom de la collection Qdrant", True, False),
        ("DATABASE_URL", "PostgreSQL (optionnel, repli SQLite)", False, True),
        ("GEMINI_API_KEY", "Clé API Gemini (LLM par défaut)", True, True),
    ]
    
    # Vérifier chaque variable
    results = []
    for var_name, description, required, sensitive in env_vars:
        value = get_env(var_name)
        if value:
            # Masquer les valeurs sensibles
            if sensitive or any(key in var_name for key in ["KEY", "PASSWORD", "TOKEN"]):
                display_value = "***"
            else:
                display_value = value
            results.append((var_name, required, "✅", display_value))
        else:
            status = "❌" if required else "ℹ️"
            results.append((var_name, required, status, "Non définie (optionnel)"))
    
    # Afficher les résultats
    print("\n📋 Variables d'environnement:")
    print("-" * 80)
    for var_name, _, status, value in results:
        print(f"{status} {var_name}: {value}")
    
    # Vérifier le fichier .env
    env_file = project_root / ".env"
    if env_file.exists():
        print(f"\n✅ Fichier .env trouvé: {env_file}")
    else:
        print(f"\n❌ Fichier .env non trouvé: {env_file}")
        print("   Créez-le avec les variables ci-dessus")
    
    # Résumé
    print("\n" + "=" * 80)
    missing = [v for v in results if v[1] and v[2] == "❌"]
    if missing:
        print("⚠️ Variables manquantes:")
        for var_name, _, _, _ in missing:
            print(f"   - {var_name}")
        print("\n📌 Configurez ces variables dans le fichier .env")
    else:
        print("✅ Toutes les variables sont configurées!")
    
    print("=" * 80)

if __name__ == "__main__":
    check_env()
