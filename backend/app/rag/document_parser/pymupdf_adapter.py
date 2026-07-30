"""
Extraction de PDFs avec PyMuPDF
"""
from pathlib import Path
import logging
from .cleaners import TextCleaner

logger = logging.getLogger(__name__)

class PyMuPDFAdapter:
    """Extraction de PDFs avec PyMuPDF."""
    
    @staticmethod
    def extract(pdf_path: Path) -> str:
        try:
            import fitz
        except ImportError:
            raise ImportError("PyMuPDF non installé. pip install pymupdf")
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF introuvable: {pdf_path}")
        
        logger.info(f"📄 PyMuPDF: {pdf_path.name}")
        
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                if page_text.strip():
                    text += f"\n\n--- Page {page_num + 1} ---\n\n"
                    text += page_text
            doc.close()
            
            text = TextCleaner.clean_text(text)
            logger.info(f"✅ {len(text)} caractères")
            return text
            
        except Exception as e:
            raise Exception(f"Erreur extraction: {e}")
