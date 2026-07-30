"""
Document Parser avec support Nougat
"""
from pathlib import Path
import logging
from .config import ParserConfig
from .pymupdf_adapter import PyMuPDFAdapter
from .nougat_adapter import NougatAdapter

logger = logging.getLogger(__name__)

class DocumentParser:
    """Parser principal avec détection automatique."""
    
    def __init__(self, use_nougat: bool = True):
        self.use_nougat = use_nougat
        self.pymupdf_adapter = PyMuPDFAdapter()
        self.nougat_adapter = NougatAdapter() if use_nougat else None
    
    def extract(self, file_path: Path, force_method: str = None) -> str:
        """Extrait le texte du document."""
        if not file_path.exists():
            raise FileNotFoundError(f"Fichier introuvable: {file_path}")
        
        # Détecter la méthode
        method = force_method or self._detect_method(file_path)
        
        logger.info(f"🔍 Méthode: {method} pour {file_path.name}")
        
        try:
            if method == "nougat" and self.nougat_adapter:
                return self.nougat_adapter.extract(file_path)
            else:
                return self.pymupdf_adapter.extract(file_path)
                
        except Exception as e:
            logger.warning(f"⚠️ Échec {method}, fallback PyMuPDF")
            return self.pymupdf_adapter.extract(file_path)
    
    def _detect_method(self, file_path: Path) -> str:
        """Détecte la méthode appropriée.

        Le corpus NURU (cours/exercices Terminale S1) est presque
        exclusivement mathématique (formules, démonstrations, tableaux) :
        conformément au cahier des charges, Nougat est donc la méthode
        privilégiée par défaut, PyMuPDF servant de repli automatique en
        cas d'indisponibilité ou d'échec (voir extract()).
        """
        if self.use_nougat and self.nougat_adapter and self.nougat_adapter.available:
            return "nougat"
        return "pymupdf"
