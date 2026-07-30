"""
Configuration du Document Parser
"""
from pathlib import Path

class ParserConfig:
    """Configuration du parser."""
    
    # Chemins
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    RAW_DIR = DATA_DIR / "raw"
    PROCESSED_DIR = DATA_DIR / "processed"
    
    # Options
    MAX_PAGES = 100
    USE_GPU = False
    USE_NOUGAT = True
    
    @classmethod
    def ensure_directories(cls):
        """Crée les dossiers nécessaires."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.RAW_DIR.mkdir(parents=True, exist_ok=True)
        cls.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        
        # Sous-dossiers
        (cls.RAW_DIR / "cours").mkdir(exist_ok=True)
        (cls.RAW_DIR / "exercices").mkdir(exist_ok=True)
        
        print(f"📁 Dossiers créés:")
        print(f"   RAW: {cls.RAW_DIR}")
        print(f"   PROCESSED: {cls.PROCESSED_DIR}")
