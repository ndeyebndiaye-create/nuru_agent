# tests/test_planner_unit.py
"""
Tests unitaires pour l'extraction du concept par le Planner.
Couvre la régression du Sprint 2 phase 4 (Test 4 du diagnostic) : le verbe
d'action ("créer") ne doit jamais rester dans le concept extrait.

Exécutez avec: pytest tests/test_planner_unit.py -v
"""
import sys
from pathlib import Path
import unittest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.agents.planner import _extract_concept


class TestExtractConcept(unittest.TestCase):

    def test_creer_quiz_verbe_infinitif(self):
        self.assertEqual(_extract_concept("créer un quiz sur les suites numériques"), "suites numériques")

    def test_creer_quiz_imperatif(self):
        self.assertEqual(_extract_concept("Crée un quiz sur les suites numériques"), "suites numériques")

    def test_fais_moi_un_exercice(self):
        self.assertEqual(_extract_concept("Fais-moi un exercice sur les intégrales"), "intégrales")

    def test_donne_moi_un_cours(self):
        self.assertEqual(_extract_concept("Donne-moi un cours sur les nombres complexes"), "nombres complexes")

    def test_explique_moi(self):
        self.assertEqual(_extract_concept("Explique-moi la dérivabilité"), "dérivabilité")

    def test_je_veux_reviser(self):
        self.assertEqual(_extract_concept("Je veux réviser les probabilités"), "probabilités")


if __name__ == "__main__":
    unittest.main()
