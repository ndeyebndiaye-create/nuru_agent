# tests/test_math_tools_unit.py
"""
Tests unitaires pour la détection d'intention mathématique et les outils SymPy.
Couvre la régression du Sprint 2 phase 4 (Test 3 du diagnostic) : un mot en
langage naturel ("dérivées") ne doit jamais être traité comme une expression
mathématique exploitable.

Exécutez avec: pytest tests/test_math_tools_unit.py -v
"""
import sys
from pathlib import Path
import unittest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.tools.math_tools import detect_math_intent, call_math_tool, MathToolError


class TestDetectMathIntentConceptual(unittest.TestCase):
    """Demandes purement conceptuelles : aucun outil ne doit être déclenché."""

    def test_explique_moi_les_derivees(self):
        self.assertIsNone(detect_math_intent("Explique-moi les dérivées"))

    def test_quest_ce_que_la_derivabilite(self):
        self.assertIsNone(detect_math_intent("Qu'est-ce que la dérivabilité ?"))

    def test_donne_moi_un_cours_sur_les_primitives(self):
        self.assertIsNone(detect_math_intent("Donne-moi un cours sur les primitives"))


class TestDetectMathIntentExplicitCalculation(unittest.TestCase):
    """Demandes de calcul explicite : l'outil SymPy doit être déclenché avec
    une expression exploitable, et produire le résultat mathématique exact."""

    def test_derive_f_x_avec_exposant_unicode(self):
        intent = detect_math_intent("Dérive f(x)=x²+3x")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["tool"], "derivee")
        result = call_math_tool(intent["tool"], expression=intent["expression"])
        self.assertEqual(result["result"], "2*x + 3")

    def test_calcule_la_derivee_de_sin(self):
        intent = detect_math_intent("Calcule la dérivée de sin(x)")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["tool"], "derivee")
        result = call_math_tool(intent["tool"], expression=intent["expression"])
        self.assertEqual(result["result"], "cos(x)")

    def test_trouve_une_primitive(self):
        intent = detect_math_intent("Trouve une primitive de 2x+1")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["tool"], "integrale")
        result = call_math_tool(intent["tool"], expression=intent["expression"])
        # x*(x+1) est la forme factorisee/simplifiee de x^2 + x, primitive de 2x+1
        self.assertEqual(result["result"], "x*(x + 1)")


class TestPluralAndConjugationDoNotFalsePositive(unittest.TestCase):
    """Formes conjuguees/plurielles proches d'un mot-cle d'action ne doivent
    pas declencher l'outil (bug d'origine : recherche de sous-chaine sans
    limite de mot, "dérivée" matchait dans "dérivées")."""

    def test_integrales_pluriel_ne_declenche_pas(self):
        self.assertIsNone(detect_math_intent("Fais-moi un exercice sur les intégrales"))


class TestSafeParseRejectsNaturalLanguage(unittest.TestCase):
    """L'outil ne doit jamais accepter une chaine qui ressemble a du texte
    naturel, meme appele directement (defense en profondeur)."""

    def test_rejette_mot_naturel(self):
        with self.assertRaises(MathToolError):
            call_math_tool("derivee", expression="dérivées")

    def test_rejette_chaine_vide(self):
        with self.assertRaises(MathToolError):
            call_math_tool("derivee", expression="   ")


if __name__ == "__main__":
    unittest.main()
