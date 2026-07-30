# tests/test_parser_unit.py
"""
Tests unitaires pour le Document Parser.
Exécutez avec: pytest tests/test_parser_unit.py -v
"""
import sys
from pathlib import Path
import unittest
import tempfile

# Ajouter le chemin du projet
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.rag.document_parser import DocumentParser, ParserConfig
from backend.app.rag.document_parser.cleaners import TextCleaner

class TestTextCleaner(unittest.TestCase):
    """Tests pour le nettoyeur de texte."""
    
    def test_clean_newlines(self):
        """Test de nettoyage des sauts de ligne."""
        text = "Ligne 1\n\n\n\nLigne 2"
        cleaned = TextCleaner.clean_newlines(text)
        self.assertEqual(cleaned, "Ligne 1\n\nLigne 2")
    
    def test_remove_headers(self):
        """Test de suppression des en-têtes."""
        text = "Page 1\nContenu principal\nPage 2\nSuite du contenu"
        cleaned = TextCleaner.remove_headers_footers(text)
        self.assertNotIn("Page 1", cleaned)
        self.assertIn("Contenu principal", cleaned)
    
    def test_fix_latex(self):
        """Test de correction LaTeX."""
        text = "$$\\frac{1}{2}$$"
        cleaned = TextCleaner.fix_latex(text)
        self.assertIn("\\[", cleaned)
        self.assertIn("\\]", cleaned)
    
    def test_full_clean(self):
        """Test du pipeline complet de nettoyage."""
        text = "Page 1\n\n\nTexte avec $$formule$$"
        cleaned = TextCleaner.clean_text(text)
        self.assertNotIn("Page 1", cleaned)
        self.assertNotIn("\n\n\n", cleaned)
        self.assertIn("formule", cleaned)

class TestDocumentParser(unittest.TestCase):
    """Tests pour le Document Parser."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.parser = DocumentParser(use_nougat=False)
        
        # Créer un fichier PDF de test si possible
        self.test_pdf = ParserConfig.RAW_DIR / "test_sample.pdf"
    
    def test_parser_initialization(self):
        """Test de l'initialisation du parser."""
        self.assertIsNotNone(self.parser)
        self.assertIsNotNone(self.parser.pymupdf_adapter)
        self.assertEqual(self.parser.use_nougat, False)
    
    def test_detect_method(self):
        """Test de détection de la méthode d'extraction."""
        # Créer des fichiers fictifs
        math_file = Path("math_derivative.pdf")
        text_file = Path("histoire_france.pdf")
        
        # Le parser devrait détecter les maths
        method_math = self.parser._detect_method(math_file)
        method_text = self.parser._detect_method(text_file)
        
        # Les deux devraient retourner "pymupdf" car use_nougat=False
        self.assertEqual(method_math, "pymupdf")
        self.assertEqual(method_text, "pymupdf")
    
    @unittest.skipIf(not Path("data/raw").exists(), "Pas de dossier raw")
    def test_parse_existing_pdf(self):
        """Test d'extraction sur un vrai PDF."""
        pdf_files = list(ParserConfig.RAW_DIR.rglob("*.pdf"))
        if not pdf_files:
            self.skipTest("Aucun PDF trouvé pour le test")
        
        pdf_path = pdf_files[0]
        text = self.parser.extract(pdf_path)
        
        self.assertIsNotNone(text)
        self.assertGreater(len(text), 10)  # Au moins 10 caractères

class TestParserConfig(unittest.TestCase):
    """Tests pour la configuration du parser."""
    
    def test_directories_creation(self):
        """Test de création des dossiers."""
        # Sauvegarder les dossiers existants
        raw_dir = ParserConfig.RAW_DIR
        processed_dir = ParserConfig.PROCESSED_DIR
        
        # Créer les dossiers (si non existants)
        ParserConfig.ensure_directories()
        
        self.assertTrue(raw_dir.exists() or raw_dir.parent.exists())
        self.assertTrue(processed_dir.exists() or processed_dir.parent.exists())
    
    def test_config_attributes(self):
        """Test des attributs de configuration."""
        self.assertIsNotNone(ParserConfig.BASE_DIR)
        self.assertIsNotNone(ParserConfig.DATA_DIR)
        self.assertIsNotNone(ParserConfig.RAW_DIR)
        self.assertIsNotNone(ParserConfig.PROCESSED_DIR)
        self.assertEqual(ParserConfig.MAX_PAGES, 100)

if __name__ == "__main__":
    unittest.main()