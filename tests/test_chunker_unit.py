# tests/test_chunker_unit.py
"""
Tests unitaires pour le chunker pédagogique.
Exécutez avec: pytest tests/test_chunker_unit.py -v
"""
import sys
from pathlib import Path
import unittest

# Ajouter le chemin du projet
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.rag.chunker import PedagogicalChunker, ChunkingPipeline, ChunkerConfig

class TestPedagogicalChunker(unittest.TestCase):
    """Tests pour le chunker pédagogique."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.config = ChunkerConfig(
            min_chunk_size=20,
            max_chunk_size=500
        )
        self.chunker = PedagogicalChunker(self.config)
        self.pipeline = ChunkingPipeline(self.config)
    
    def test_chunk_detection(self):
        """Test de détection des types de chunks."""
        text = "# Chapitre 1 : Test\n**Définition 1 :** Une définition."
        lines = text.split('\n')
        
        for line in lines:
            detected = self.chunker._detect_section_type(line)
            if "Chapitre" in line:
                self.assertEqual(detected, "chapitre")
            elif "Définition" in line:
                self.assertEqual(detected, "definition")
    
    def test_chunking_pipeline(self):
        """Test du pipeline complet."""
        text = """
# Chapitre 1 : Test

**Définition 1 :** Une définition simple.

**Exercice 1 :** Un exercice.
"""
        metadata = {"source": "test.md"}
        
        chunks = self.pipeline.process(text, metadata)
        
        # Vérifier qu'on a des chunks
        self.assertTrue(len(chunks) > 0)
        
        # Vérifier les métadonnées
        for chunk in chunks:
            self.assertIn("text", chunk)
            self.assertIn("chunk_type", chunk)
            self.assertIn("metadata", chunk)
    
    def test_math_detection(self):
        """Test de détection des mathématiques."""
        text = "La formule est $\\frac{1}{2}$ et $\\sqrt{4}=2$."
        chunk = self.chunker.chunk(text, {})[0]
        
        self.assertTrue(chunk.metadata.get("has_formulas", False))
        self.assertGreater(chunk.metadata.get("formula_count", 0), 0)
    
    def test_competence_extraction(self):
        """Test d'extraction des compétences."""
        text = "Calculer la dérivée de f(x) = x². Résoudre l'équation."
        chunk = self.chunker.chunk(text, {})[0]
        
        competences = chunk.metadata.get("competences", [])
        self.assertIn("calculer", competences)
        self.assertIn("résoudre", competences)
    
    def test_difficulty_estimation(self):
        """Test d'estimation de la difficulté."""
        # Texte simple
        simple_text = "Un texte court et simple."
        chunk = self.chunker.chunk(simple_text, {})[0]
        self.assertEqual(chunk.metadata.get("difficulty_level"), "basic")
        
        # Texte complexe avec formules
        complex_text = "Théorème: $\\frac{d}{dx}x^n = nx^{n-1}$" * 20
        chunk = self.chunker.chunk(complex_text, {})[0]
        self.assertEqual(chunk.metadata.get("difficulty_level"), "advanced")

class TestChunkerConfig(unittest.TestCase):
    """Tests pour la configuration du chunker."""
    
    def test_default_config(self):
        """Test de la configuration par défaut."""
        config = ChunkerConfig()
        self.assertEqual(config.min_chunk_size, 100)
        self.assertEqual(config.max_chunk_size, 1500)
        self.assertIn("definition", config.section_patterns)
    
    def test_custom_config(self):
        """Test de la configuration personnalisée."""
        config = ChunkerConfig(
            min_chunk_size=50,
            max_chunk_size=800,
            default_metadata={"auteur": "Test"}
        )
        self.assertEqual(config.min_chunk_size, 50)
        self.assertEqual(config.max_chunk_size, 800)
        self.assertEqual(config.default_metadata["auteur"], "Test")

if __name__ == "__main__":
    unittest.main()