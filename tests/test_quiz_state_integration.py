# tests/test_quiz_state_integration.py
"""
Test d'intégration : une conversation de quiz en plusieurs tours doit
conserver l'état actif du quiz (question courante, choix, bonne réponse) et
interpréter la réponse de l'élève comme une correction, pas comme une
nouvelle question générale (Sprint 2 phase 4, Test 4 du diagnostic).

Exécutez avec: pytest tests/test_quiz_state_integration.py -v
"""
import sys
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.api.routes import chat as chat_routes
from backend.app.api.models.requests import ChatRequest


def _make_two_question_quiz():
    return {
        "concept": "suites numériques",
        "chapitre": None,
        "questions": [
            {
                "question": "Une suite arithmétique a une raison constante : vrai ou faux ?",
                "choices": [{"id": "A", "text": "Vrai"}, {"id": "B", "text": "Faux"}],
                "correct_answer": "A",
                "explanation": "La bonne réponse est A : Vrai. Par définition, une suite arithmétique ajoute la même raison à chaque terme.",
            },
            {
                "question": "Quelle est la raison de la suite 2, 5, 8, 11 ?",
                "choices": [{"id": "A", "text": "2"}, {"id": "B", "text": "3"}, {"id": "C", "text": "5"}, {"id": "D", "text": "8"}],
                "correct_answer": "B",
                "explanation": "La bonne réponse est B : 3. Chaque terme augmente de 3 (5-2=3, 8-5=3, 11-8=3).",
            },
        ],
        "current_index": 0,
        "attempts": 0,
    }


class TestActiveQuizConversation(unittest.TestCase):

    def setUp(self):
        self.session = {"created_at": "now", "history": [], "active_quiz": _make_two_question_quiz()}

    def test_first_answer_correct_moves_to_next_question(self):
        result = chat_routes._handle_active_quiz_answer(self.session, student_id=None, session_id="s1", message="A")

        self.assertEqual(result["intent"], "quiz_answer")
        self.assertIn("Bonne réponse", result["response"])
        # Le quiz doit encore etre actif (2eme question restante)
        self.assertIn("active_quiz", self.session)
        self.assertEqual(self.session["active_quiz"]["current_index"], 1)
        # La question suivante doit etre proposee dans la reponse
        self.assertIn("raison de la suite", result["response"])

    def test_second_answer_wrong_reveals_correct_and_ends_quiz(self):
        # Premier tour (consomme la question 1)
        chat_routes._handle_active_quiz_answer(self.session, student_id=None, session_id="s1", message="A")
        # Deuxieme tour : reponse incorrecte a la question 2
        result = chat_routes._handle_active_quiz_answer(self.session, student_id=None, session_id="s1", message="D")

        self.assertIn("Pas tout à fait", result["response"])
        self.assertIn("B", result["response"])  # la bonne reponse est revelee apres coup
        self.assertIn("B : 3", result["response"])
        # Le quiz est termine : l'etat actif doit avoir ete retire de la session
        self.assertNotIn("active_quiz", self.session)
        self.assertIn("terminé", result["response"])

    def test_answer_by_numeric_position_is_accepted(self):
        # L'eleve tape "1" (position) au lieu de la lettre "A" (bug original :
        # "1" etait traite comme une toute nouvelle question generale).
        result = chat_routes._handle_active_quiz_answer(self.session, student_id=None, session_id="s1", message="1")
        self.assertIn("Bonne réponse", result["response"])

    def test_a_new_quiz_response_from_orchestrator_is_stored_as_active(self):
        session = {"created_at": "now", "history": []}
        quiz_response = {
            "concept": "suites numériques",
            "questions": _make_two_question_quiz()["questions"],
        }
        # Reproduit la logique de stockage appliquee dans chat() apres l'appel
        # a l'orchestrateur (voir routes/chat.py).
        if quiz_response and quiz_response.get("questions"):
            session["active_quiz"] = {
                "concept": quiz_response.get("concept"),
                "chapitre": None,
                "questions": quiz_response["questions"],
                "current_index": 0,
                "attempts": 0,
            }
        self.assertIn("active_quiz", session)
        self.assertEqual(session["active_quiz"]["current_index"], 0)


class TestQuizSessionAcrossTwoRequests(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        chat_routes.sessions.clear()

    def tearDown(self):
        chat_routes.sessions.clear()

    async def test_same_session_uses_stored_correct_option_and_explanation(self):
        session_id = "quiz-two-requests"
        question = _make_two_question_quiz()["questions"][1]
        orchestrator = Mock()
        orchestrator.process.return_value = {
            "response": "Question de quiz affichée",
            "intent": "quiz",
            "level": "reformulation",
            "confidence": 1.0,
            "responses": {
                "quiz": {
                    "concept": "suites numériques",
                    "questions": [question],
                }
            },
            "math_tool_result": None,
            "progression_summary": {},
            "timestamp": "2026-07-17T00:00:00",
        }

        with (
            patch.object(chat_routes, "get_orchestrator", return_value=orchestrator),
            patch.object(chat_routes, "_get_student_id", return_value=None),
        ):
            first = await chat_routes.chat(ChatRequest(
                message="Fais-moi un quiz",
                session_id=session_id,
                user_id="student-test",
            ))

            stored_question = chat_routes.sessions[session_id]["active_quiz"]["questions"][0]
            self.assertEqual(first["session_id"], session_id)
            self.assertEqual(stored_question["correct_answer"], "B")
            self.assertIn("B : 3", stored_question["explanation"])

            second = await chat_routes.chat(ChatRequest(
                message="B",
                session_id=session_id,
                user_id="student-test",
            ))

        orchestrator.process.assert_called_once()
        self.assertEqual(second["session_id"], session_id)
        self.assertEqual(second["intent"], "quiz_answer")
        self.assertIn("Bonne réponse", second["response"])
        self.assertIn("B : 3", second["response"])
        self.assertNotIn("active_quiz", chat_routes.sessions[session_id])


if __name__ == "__main__":
    unittest.main()
