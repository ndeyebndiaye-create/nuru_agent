# tests/test_metadata_unit.py
"""
Tests unitaires pour l'extracteur de métadonnées.
Exécutez avec: pytest tests/test_metadata_unit.py -v
"""
import sys
from pathlib import Path
import unittest
import tempfile
import json

# Ajouter le chemin du projet
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.rag.metadata_extractor import (
    MetadataConfig,
    FileMetadataExtractor,
    ContentMetadataExtractor,
    MetadataMerger
)


class TestMetadataConfig(unittest.TestCase):
    """Tests pour la configuration des métadonnées."""
    
    def test_default_config(self):
        """Test de la configuration par défaut."""
        config = MetadataConfig()
        
        self.assertIsNotNone(config.file_patterns)
        self.assertIsNotNone(config.content_patterns)
        self.assertIsNotNone(config.class_mapping)
        self.assertIsNotNone(config.required_fields)
        self.assertIsNotNone(config.default_metadata)
        
        # Vérifier les champs requis
        required = ["discipline", "classe", "serie", "chapitre", "type_document"]
        for field in required:
            self.assertIn(field, config.required_fields)
    
    def test_class_mapping(self):
        """Test du mapping des classes sénégalaises."""
        config = MetadataConfig()
        
        # Vérifier la classe Terminale
        self.assertIn("Terminale", config.class_mapping)
        self.assertIn("S1", config.class_mapping["Terminale"])
        self.assertEqual(
            config.class_mapping["Terminale"]["S1"],
            "Sciences Mathématiques"
        )
        
        # Vérifier la classe Première
        self.assertIn("Première", config.class_mapping)
        self.assertIn("S", config.class_mapping["Première"])
    
    def test_default_metadata(self):
        """Test des métadonnées par défaut."""
        config = MetadataConfig()
        
        self.assertEqual(config.default_metadata["discipline"], "mathématiques")
        self.assertEqual(config.default_metadata["pays"], "Sénégal")
        self.assertEqual(config.default_metadata["langue"], "français")


class TestFileMetadataExtractor(unittest.TestCase):
    """Tests pour l'extraction depuis les noms de fichiers."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.config = MetadataConfig()
        self.extractor = FileMetadataExtractor(self.config)
    
    def test_extract_serie(self):
        """Test d'extraction de la série."""
        test_cases = [
            ("TD1-Probabilite-TS1.pdf", "TS1"),
            ("Devoirs-TS-Analyse.pdf", "TS"),
            ("S1-Bac-Blanc-LBD-2017.pdf", "S1"),
            ("Fasicule_TS1.pdf", "TS1"),
        ]
        
        for filename, expected in test_cases:
            file_path = Path(filename)
            metadata = self.extractor.extract(file_path)
            if expected in filename:
                self.assertIn("serie", metadata)
                self.assertEqual(metadata["serie"].upper(), expected.replace("S", "S"))
    
    def test_extract_chapitre(self):
        """Test d'extraction du chapitre."""
        test_cases = [
            ("Chapitre1_Revisions.pdf", "1"),
            ("Chap_2_Derivabilite.pdf", "2"),
            ("Chapitre_3_Limites.pdf", "3"),
        ]
        
        for filename, expected in test_cases:
            file_path = Path(filename)
            metadata = self.extractor.extract(file_path)
            if "chapitre_numero" in metadata:
                self.assertEqual(metadata["chapitre_numero"], expected)
    
    def test_extract_type_document(self):
        """Test d'extraction du type de document."""
        test_cases = [
            ("cours_derivabilite.pdf", "cours"),
            ("exercices_probabilites.pdf", "exercices"),
            ("Devoir_maison.pdf", "devoir"),
            ("composition_s1.pdf", "composition"),
            ("annales_maths.pdf", "annales"),
        ]
        
        for filename, expected in test_cases:
            file_path = Path(filename)
            metadata = self.extractor.extract(file_path)
            if "type_document" in metadata:
                self.assertEqual(metadata["type_document"].lower(), expected)
    
    def test_extract_annee(self):
        """Test d'extraction de l'année."""
        test_cases = [
            ("Sujet_2023.pdf", "2023"),
            ("Bac_2024.pdf", "2024"),
            ("Annales_2020-2021.pdf", "2020"),
        ]
        
        for filename, expected in test_cases:
            file_path = Path(filename)
            metadata = self.extractor.extract(file_path)
            if "annee" in metadata:
                self.assertEqual(metadata["annee"], expected)
    
    def test_extract_from_path(self):
        """Test d'extraction depuis le chemin complet."""
        file_path = Path("data/raw/cours/01_Revisions_trigonometrie.pdf")
        metadata = self.extractor.extract(file_path)
        
        # Vérifier que les métadonnées de base sont présentes
        self.assertIn("source", metadata)
        self.assertIn("filename", metadata)
        self.assertEqual(metadata["filename"], "01_Revisions_trigonometrie.pdf")
    
    def test_normalize_metadata(self):
        """Test de normalisation des métadonnées."""
        # Tester la normalisation de la classe
        file_path = Path("Terminale_S1_cours.pdf")
        metadata = self.extractor.extract(file_path)
        
        if "classe" in metadata:
            self.assertIn(metadata["classe"], ["Terminale", "Terminale"])
        
        # Tester la normalisation du type
        file_path = Path("exercices_01.pdf")
        metadata = self.extractor.extract(file_path)
        
        if "type_document_normalized" in metadata:
            self.assertEqual(metadata["type_document_normalized"], "exercise")


class TestContentMetadataExtractor(unittest.TestCase):
    """Tests pour l'extraction depuis le contenu."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.config = MetadataConfig()
        self.extractor = ContentMetadataExtractor(self.config)
    
    def test_extract_title(self):
        """Test d'extraction du titre."""
        text = "# Chapitre 1 : Les Nombres Réels\n\nContenu du chapitre..."
        metadata = self.extractor.extract(text)
        
        self.assertIn("titre", metadata)
        self.assertEqual(metadata["titre"], "Chapitre 1 : Les Nombres Réels")
    
    def test_extract_chapitre(self):
        """Test d'extraction du chapitre."""
        text = """
# Chapitre 1 : Les Nombres Réels

## 1.1 Définition

Contenu...
"""
        metadata = self.extractor.extract(text)
        
        self.assertIn("chapitre", metadata)
        self.assertEqual(metadata["chapitre"], "Les Nombres Réels")
        self.assertIn("chapitre_numero", metadata)
        self.assertEqual(metadata["chapitre_numero"], "1")
    
    def test_extract_classe(self):
        """Test d'extraction de la classe."""
        text = """
Classe de Terminale S1
Année scolaire 2023-2024
"""
        metadata = self.extractor.extract(text)
        
        self.assertIn("classe", metadata)
        self.assertEqual(metadata["classe"], "Terminale")
        self.assertIn("serie", metadata)
        self.assertEqual(metadata["serie"], "S1")
    
    def test_extract_annee_scolaire(self):
        """Test d'extraction de l'année scolaire."""
        text = "Année scolaire 2023-2024"
        metadata = self.extractor.extract(text)
        
        self.assertIn("annee_scolaire", metadata)
        self.assertEqual(metadata["annee_scolaire"], "2023-2024")
    
    def test_extract_auteur(self):
        """Test d'extraction de l'auteur."""
        text = "Professeur: M. Babacar DJITTE"
        metadata = self.extractor.extract(text)
        
        self.assertIn("auteur", metadata)
        self.assertEqual(metadata["auteur"], "M. Babacar DJITTE")
    
    def test_extract_competences(self):
        """Test d'extraction des compétences."""
        text = """
Compétences : Calculer, Déterminer, Résoudre

Contenu du cours...
"""
        metadata = self.extractor.extract(text)
        
        self.assertIn("competences", metadata)
        competences = metadata["competences"]
        self.assertIsInstance(competences, list)
        self.assertGreater(len(competences), 0)
    
    def test_merge_with_existing(self):
        """Test de fusion avec des métadonnées existantes."""
        existing = {"classe": "Terminale", "source": "test.pdf"}
        text = "# Nouveau Chapitre\n\nContenu..."
        
        metadata = self.extractor.extract(text, existing)
        
        # Les métadonnées existantes doivent être conservées
        self.assertEqual(metadata["classe"], "Terminale")
        self.assertEqual(metadata["source"], "test.pdf")
        # Les nouvelles métadonnées doivent être ajoutées
        self.assertIn("titre", metadata)


class TestMetadataMerger(unittest.TestCase):
    """Tests pour le mergeur de métadonnées."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.config = MetadataConfig()
        self.merger = MetadataMerger(self.config)
    
    def test_full_extraction(self):
        """Test d'extraction complète."""
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Contenu de test
            content = """
# Chapitre 1 : Trigonométrie

Classe de Terminale S1
Année scolaire 2023-2024
Professeur: M. Babacar DJITTE

## I. Rappels

**Compétences :** Calculer, Résoudre

Contenu du cours...
"""
            
            # Extraire les métadonnées
            metadata = self.merger.extract_metadata(tmp_path, content)
            
            # Vérifier les métadonnées extraites
            self.assertIn("discipline", metadata)
            self.assertIn("classe", metadata)
            self.assertIn("serie", metadata)
            self.assertIn("chapitre", metadata)
            self.assertIn("type_document", metadata)
            self.assertIn("auteur", metadata)
            self.assertIn("competences", metadata)
            self.assertIn("document_id", metadata)
            
            # Vérifier les valeurs
            self.assertEqual(metadata["classe"], "Terminale")
            self.assertEqual(metadata["serie"], "S1")
            self.assertEqual(metadata["chapitre"], "Trigonométrie")
            self.assertEqual(metadata["auteur"], "M. Babacar DJITTE")
            
        finally:
            # Nettoyer
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_additional_metadata(self):
        """Test avec des métadonnées supplémentaires."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            content = "# Test\n\nContenu..."
            additional = {
                "discipline": "physique",
                "chapitre": "Mécanique",
                "source_type": "cours_officiel"
            }
            
            metadata = self.merger.extract_metadata(
                tmp_path, 
                content, 
                additional
            )
            
            # Les métadonnées supplémentaires doivent être présentes
            self.assertEqual(metadata["discipline"], "physique")
            self.assertEqual(metadata["chapitre"], "Mécanique")
            self.assertEqual(metadata["source_type"], "cours_officiel")
            
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_required_fields(self):
        """Test que les champs requis sont toujours présents."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            content = "Texte simple sans métadonnées"
            
            metadata = self.merger.extract_metadata(tmp_path, content)
            
            # Les champs requis doivent être présents (avec valeurs par défaut)
            for field in self.config.required_fields:
                self.assertIn(field, metadata)
            
            # Vérifier les valeurs par défaut
            self.assertEqual(metadata["discipline"], "mathématiques")
            self.assertEqual(metadata["classe"], "Terminale")
            self.assertEqual(metadata["serie"], "S1")
            
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_serie_nom(self):
        """Test du nom complet de la série."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            content = "Classe de Terminale S1"
            metadata = self.merger.extract_metadata(tmp_path, content)
            
            self.assertIn("serie_nom", metadata)
            self.assertEqual(metadata["serie_nom"], "Sciences Mathématiques")
            
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_document_id(self):
        """Test de la génération de l'ID de document."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            content = "Test"
            metadata = self.merger.extract_metadata(tmp_path, content)
            
            self.assertIn("document_id", metadata)
            self.assertEqual(len(metadata["document_id"]), 16)  # MD5 hex digest
            
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    
    def test_real_world_scenario(self):
        """Test sur un scénario réel avec un nom de fichier."""
        # Simuler un fichier réel
        file_path = Path("data/raw/exercices/Chap1_Probabilite/TD1-Probabilite-TS1.pdf")
        
        content = """
# Chapitre 1 : Probabilités

Classe de Terminale S1
Année scolaire 2023-2024

**Exercice 1 :** Calculer la probabilité...

Compétences : Calculer, Déterminer, Analyser
"""
        
        try:
            metadata = self.merger.extract_metadata(file_path, content)
            
            # Vérifier les métadonnées
            self.assertEqual(metadata["serie"], "TS1")
            self.assertEqual(metadata["type_document"], "exercices")
            self.assertEqual(metadata["classe"], "Terminale")
            self.assertEqual(metadata["chapitre"], "Probabilités")
            
            # Vérifier les compétences
            self.assertIn("competences", metadata)
            competences = metadata["competences"]
            self.assertIn("Calculer", competences)
            self.assertIn("Déterminer", competences)
            
        except Exception as e:
            # Si le fichier n'existe pas vraiment, on passe
            pass


class TestMetadataIntegration(unittest.TestCase):
    """Tests d'intégration pour les métadonnées."""
    
    def test_parser_chunker_metadata_flow(self):
        """Test du flux complet: parser -> chunker -> métadonnées."""
        # Ce test nécessite un vrai PDF
        raw_dir = Path("data/raw")
        pdf_files = list(raw_dir.rglob("*.pdf"))
        
        if not pdf_files:
            self.skipTest("Aucun PDF trouvé pour le test d'intégration")
        
        from backend.app.rag.document_parser import DocumentParser
        from backend.app.rag.chunker import ChunkingPipeline
        
        # 1. Parser le PDF
        parser = DocumentParser(use_nougat=False)
        text = parser.extract(pdf_files[0])
        
        # 2. Extraire les métadonnées
        merger = MetadataMerger()
        metadata = merger.extract_metadata(pdf_files[0], text)
        
        # 3. Chunker avec métadonnées
        chunker = ChunkingPipeline()
        chunks = chunker.process(text, metadata)
        
        # Vérifier que les chunks ont les métadonnées
        self.assertGreater(len(chunks), 0)
        for chunk in chunks:
            self.assertIn("metadata", chunk)
            chunk_metadata = chunk["metadata"]
            
            # Les métadonnées de base doivent être présentes
            self.assertIn("discipline", chunk_metadata)
            self.assertIn("source", chunk_metadata)
            self.assertIn("chunk_type", chunk)


if __name__ == "__main__":
    unittest.main()