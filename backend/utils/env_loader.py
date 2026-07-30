# backend/utils/env_loader.py
"""
Charge les variables d'environnement depuis le fichier .env
"""
import os
from pathlib import Path
from dotenv import load_dotenv

def load_env():
    """
    Charge les variables d'environnement.
    """
    # Chemin du fichier .env
    env_path = Path(__file__).parent.parent.parent / ".env"
    
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Fichier .env chargé: {env_path}")
    else:
        print(f"⚠️ Fichier .env non trouvé: {env_path}")
        print("   Créez-le avec les variables nécessaires")

def get_env(key: str, default: str = None) -> str:
    """
    Récupère une variable d'environnement.
    """
    return os.getenv(key, default)

# Charger automatiquement
load_env()