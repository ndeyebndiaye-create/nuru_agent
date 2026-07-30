# tests/test_integration.py
"""
Tests d'intégration : parser + chunker ensemble.
"""
import sys
from pathlib import Path
import unittest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.rag.document_parser.parser import DocumentParser
from backend.app.rag.chunker import ChunkingPipeline

class TestParserChunkerIntegration(unittest.TestCase):
    """Test de l'intégration parser + chunker."""
    
    def test_parser_to_chunker(self):
        """Test du flux complet parser -> chunker."""
        # Créer un fichier de test simple
        test_dir = Path("data/raw")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Ce test nécessite un vrai fichier PDF
        # Pour l'instant, on le marque comme skip si pas de PDF
        pdf_files = list(test_dir.glob("*.pdf"))
        if not pdf_files:
            self.skipTest("Aucun fichier PDF trouvé pour l'intégration")
        
        # Parser
        parser = DocumentParser(use_nougat=False)
        text = parser.extract(pdf_files[0])
        
        # Chunker
        chunker = ChunkingPipeline()
        metadata = {
            "source": str(pdf_files[0]),
            "discipline": "mathématiques"
        }
        chunks = chunker.process(text, metadata)
        
        # Vérifications
        self.assertTrue(len(chunks) > 0)
        for chunk in chunks:
            self.assertIn("text", chunk)
            self.assertIn("metadata", chunk)
            self.assertGreater(len(chunk["text"]), 10)

if __name__ == "__main__":
    unittest.main()