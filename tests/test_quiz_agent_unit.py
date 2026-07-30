# tests/test_quiz_agent_unit.py
"""
Tests unitaires pour l'agent Quiz : parsing du JSON structuré renvoyé par le
LLM et rejet de tout contenu placeholder (Sprint 2 phase 4, Test 4).

Exécutez avec: pytest tests/test_quiz_agent_unit.py -v
"""
import sys
from pathlib import Path
from unittest.mock import patch
import unittest

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.agents.evaluation_agent import EvaluationAgent
from backend.app.agents.quiz_agent import QuizAgent, _contains_placeholder


VALID_QUIZ_JSON = """
{"question": "Quelle est la limite de la suite u_n = 1/n quand n tend vers l'infini ?",
 "choices": [{"id": "A", "text": "0"}, {"id": "B", "text": "1"}, {"id": "C", "text": "l'infini"}, {"id": "D", "text": "n'existe pas"}],
 "correct_answer": "A",
 "explanation": "1/n tend vers 0 quand n devient grand."}
"""

PLACEHOLDER_QUIZ_JSON = """
{"question": "Que signifie suites numériques ?",
 "choices": [{"id": "A", "text": "Définition correcte de suites numériques"}, {"id": "B", "text": "Définition incorrecte 1"}, {"id": "C", "text": "Définition incorrecte 2"}, {"id": "D", "text": "Définition incorrecte 3"}],
 "correct_answer": "A",
 "explanation": ""}
"""

INCONSISTENT_EXPLANATION_QUIZ_JSON = """
{"question": "Quelle dérivée décrit le taux de variation instantané ?",
 "choices": [{"id": "A", "text": "La dérivée seconde"}, {"id": "B", "text": "La dérivée première"}],
 "correct_answer": "A",
 "explanation": "La dérivée première décrit le taux de variation instantané."}
"""


class TestContainsPlaceholder(unittest.TestCase):

    def test_detects_definition_correcte(self):
        self.assertTrue(_contains_placeholder("Définition correcte de suites numériques"))

    def test_detects_option_pattern(self):
        self.assertTrue(_contains_placeholder("Option 1"))

    def test_valid_content_not_flagged(self):
        self.assertFalse(_contains_placeholder("La limite de 1/n est 0 quand n tend vers l'infini."))


class TestParseQuizJson(unittest.TestCase):

    def setUp(self):
        self.agent = QuizAgent()

    def test_parses_valid_json(self):
        parsed = self.agent._parse_quiz_json(VALID_QUIZ_JSON)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["correct_answer"], "A")
        self.assertEqual(len(parsed["choices"]), 4)

    def test_parses_json_wrapped_in_markdown(self):
        wrapped = f"Voici le quiz demandé :\n```json\n{VALID_QUIZ_JSON}\n```\nJ'espère que ça aide !"
        parsed = self.agent._parse_quiz_json(wrapped)
        self.assertIsNotNone(parsed)

    def test_rejects_malformed_json(self):
        self.assertIsNone(self.agent._parse_quiz_json("Ceci n'est pas du JSON."))

    def test_rejects_missing_correct_answer(self):
        broken = '{"question": "Q ?", "choices": [{"id": "A", "text": "x"}, {"id": "B", "text": "y"}]}'
        self.assertIsNone(self.agent._parse_quiz_json(broken))

    def test_rejects_correct_answer_not_in_choices(self):
        broken = (
            '{"question": "Q ?", "choices": [{"id": "A", "text": "x"}, {"id": "B", "text": "y"}], '
            '"correct_answer": "Z"}'
        )
        self.assertIsNone(self.agent._parse_quiz_json(broken))

    def test_replaces_explanation_that_justifies_another_option(self):
        parsed = self.agent._parse_quiz_json(INCONSISTENT_EXPLANATION_QUIZ_JSON)

        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["correct_answer"], "A")
        self.assertIn("A : La dérivée seconde", parsed["explanation"])
        self.assertNotIn("La dérivée première décrit", parsed["explanation"])

    def test_evaluation_compares_student_answer_to_same_correct_option(self):
        parsed = self.agent._parse_quiz_json(INCONSISTENT_EXPLANATION_QUIZ_JSON)
        evaluator = EvaluationAgent()

        correct = evaluator.evaluate_quiz("dérivées", [parsed], ["A"])
        incorrect = evaluator.evaluate_quiz("dérivées", [parsed], ["B"])

        self.assertEqual(correct["detail"][0]["expected"], "A")
        self.assertTrue(correct["detail"][0]["is_correct"])
        self.assertFalse(incorrect["detail"][0]["is_correct"])


class TestGenerateNeverReturnsPlaceholder(unittest.TestCase):
    """Meme si le LLM renvoie un contenu de type gabarit (ou echoue), le quiz
    affiche a l'eleve ne doit jamais contenir de placeholder."""

    def setUp(self):
        self.agent = QuizAgent()

    @patch("backend.app.agents.quiz_agent.generate_pedagogical_text")
    def test_llm_returns_placeholder_content_is_rejected(self, mock_generate):
        mock_generate.return_value = PLACEHOLDER_QUIZ_JSON
        result = self.agent.generate(state=None, context={"concept": "suites numériques", "quiz_type": "qcm"})
        self.assertEqual(result["questions"], [])
        self.assertIn("n'a pas pu être généré", result["instructions"])

    @patch("backend.app.agents.quiz_agent.generate_pedagogical_text")
    def test_llm_returns_valid_quiz_is_accepted(self, mock_generate):
        mock_generate.return_value = VALID_QUIZ_JSON
        result = self.agent.generate(state=None, context={"concept": "suites numériques", "quiz_type": "qcm"})
        self.assertEqual(len(result["questions"]), 1)
        self.assertNotIn("correct", str(result["questions"]).lower().replace("correct_answer", ""))

    @patch("backend.app.agents.quiz_agent.generate_pedagogical_text")
    def test_llm_unavailable_returns_empty_not_fake_quiz(self, mock_generate):
        mock_generate.return_value = "⚠️ LLM indisponible pour le moment. Réessaie plus tard."
        result = self.agent.generate(state=None, context={"concept": "suites numériques", "quiz_type": "qcm"})
        self.assertEqual(result["questions"], [])


if __name__ == "__main__":
    unittest.main()
