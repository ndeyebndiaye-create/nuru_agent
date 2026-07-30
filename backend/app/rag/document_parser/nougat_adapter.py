"""
Extraction de PDFs mathématiques avec Nougat
"""
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class NougatAdapter:
    """Extraction avec Nougat pour les formules mathématiques."""
    
    def __init__(self, model_name: str = "facebook/nougat-base"):
        self.model_name = model_name
        self.available = self._check_availability()
        self.model = None
    
    def _check_availability(self) -> bool:
        """Vérifie si Nougat est disponible."""
        try:
            import nougat
            return True
        except ImportError:
            logger.warning("⚠️ Nougat non installé")
            logger.info("   Installez avec: pip install nougat-ocr")
            return False
    
    def _load_model(self):
        """Charge le modèle Nougat."""
        if self.model is not None:
            return
        
        if not self.available:
            return
        
        try:
            from nougat import NougatModel
            import torch
            
            logger.info(f"🔄 Chargement de Nougat: {self.model_name}")
            self.model = NougatModel.from_pretrained(self.model_name)
            
            if torch.cuda.is_available():
                self.model = self.model.cuda()
                logger.info("✅ Nougat chargé sur GPU")
            else:
                logger.info("✅ Nougat chargé sur CPU")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement Nougat: {e}")
            self.available = False
    
    def extract(self, pdf_path: Path) -> str:
        """Extrait le texte et les formules avec Nougat."""
        if not self.available:
            return self._fallback_extract(pdf_path)
        
        try:
            self._load_model()
            
            logger.info(f"📄 Nougat extraction: {pdf_path.name}")
            
            # Prédiction
            result = self.model.predict(pdf_path)
            
            # Nettoyage
            text = self._clean_output(result)
            
            logger.info(f"✅ {len(text)} caractères extraits")
            return text
            
        except Exception as e:
            logger.error(f"❌ Erreur Nougat: {e}")
            return self._fallback_extract(pdf_path)
    
    def _clean_output(self, text: str) -> str:
        """Nettoie la sortie Nougat."""
        lines = text.split('\n')
        cleaned = []
        
        for line in lines:
            # Garder les formules LaTeX
            if '$' in line or '\\[' in line or '\\]' in line:
                cleaned.append(line)
            elif line.strip() and not line.strip().startswith('#'):
                cleaned.append(line)
        
        return '\n'.join(cleaned)
    
    def _fallback_extract(self, pdf_path: Path) -> str:
        """Extraction de secours avec PyMuPDF."""
        try:
            import fitz
            logger.info(f"📄 Fallback PyMuPDF: {pdf_path.name}")
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            logger.error(f"❌ Erreur fallback: {e}")
            return f"PDF: {pdf_path.name} (extraction impossible)"
    
    def extract_batch(self, pdf_paths: list, output_dir: Path = None) -> dict:
        """Extraction batch."""
        results = {}
        for pdf_path in pdf_paths:
            try:
                text = self.extract(pdf_path)
                results[str(pdf_path)] = text
                
                if output_dir:
                    output_dir.mkdir(parents=True, exist_ok=True)
                    out_file = output_dir / f"{pdf_path.stem}_nougat.md"
                    with open(out_file, 'w', encoding='utf-8') as f:
                        f.write(text)
                    logger.info(f"💾 Sauvegardé: {out_file}")
                    
            except Exception as e:
                logger.error(f"❌ Erreur {pdf_path.name}: {e}")
                results[str(pdf_path)] = f"Erreur: {e}"
        
        return results
