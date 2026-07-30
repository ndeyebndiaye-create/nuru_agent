# backend/app/agents/evaluation_agent.py
"""
Agent Evaluation - analyse les résultats d'exercices/quiz pour identifier
les erreurs, les compétences faibles et proposer des recommandations.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .config import AgentConfig

logger = logging.getLogger(__name__)


def _answers_match(student_answer: Any, expected: Any, choices: Optional[List[Dict[str, Any]]]) -> bool:
    """Compare la réponse brute de l'élève (lettre "A", chiffre "1", ou texte
    du choix) à l'identifiant de la bonne réponse (ex: "A"), sans supposer
    que l'élève tape exactement le même format que celui stocké."""
    if student_answer is None or expected is None:
        return False

    student_norm = str(student_answer).strip().lower()
    expected_norm = str(expected).strip().lower()

    if student_norm == expected_norm:
        return True

    if choices:
        # Reponse donnee par position numerique (1 = premier choix, etc.)
        if student_norm.isdigit():
            index = int(student_norm) - 1
            if 0 <= index < len(choices) and str(choices[index].get("id", "")).strip().lower() == expected_norm:
                return True
        # Reponse donnee par le texte du choix plutot que son identifiant
        for choice in choices:
            if str(choice.get("id", "")).strip().lower() == expected_norm:
                if student_norm == str(choice.get("text", "")).strip().lower():
                    return True

    return False


class EvaluationAgent:
    """Analyse la performance de l'élève sur un exercice ou un quiz."""

    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()

    def evaluate_quiz(
        self,
        concept: str,
        questions: List[Dict[str, Any]],
        student_answers: List[Any],
    ) -> Dict[str, Any]:
        """Corrige un quiz QCM/Vrai-Faux et calcule un score.

        `questions` doit correspondre au format produit par QuizAgent :
        `correct_answer` (id de choix, ex: "A") pour le format JSON structuré
        actuel, avec repli sur les anciennes clés `correct`/`answer` pour la
        compatibilité avec d'éventuelles données déjà enregistrées.
        """
        total = len(questions)
        correct_count = 0
        detail: List[Dict[str, Any]] = []

        for i, question in enumerate(questions):
            student_answer = student_answers[i] if i < len(student_answers) else None
            expected = question.get("correct_answer", question.get("correct", question.get("answer")))
            is_correct = _answers_match(student_answer, expected, question.get("choices"))

            if is_correct:
                correct_count += 1

            detail.append({
                "question": question.get("question"),
                "expected": expected,
                "student_answer": student_answer,
                "is_correct": is_correct,
            })

        score = correct_count / total if total else 0.0

        return {
            "type": "evaluation_quiz",
            "concept": concept,
            "score": round(score, 2),
            "correct_count": correct_count,
            "total": total,
            "detail": detail,
            "weak": score < self.config.confidence_threshold,
            "recommendations": self._recommendations(concept, score, detail),
        }

    def evaluate_exercise(
        self,
        concept: str,
        is_correct: bool,
        student_answer: Optional[str] = None,
        expected_answer: Optional[str] = None,
        error_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Évalue une réponse libre d'exercice (correction déclarée par
        l'agent Exercices ou par un enseignant)."""
        return {
            "type": "evaluation_exercice",
            "concept": concept,
            "is_correct": is_correct,
            "student_answer": student_answer,
            "expected_answer": expected_answer,
            "error_type": error_type,
            "recommendations": self._recommendations(concept, 1.0 if is_correct else 0.0, []),
        }

    def _recommendations(self, concept: str, score: float, detail: List[Dict[str, Any]]) -> List[str]:
        recs: List[str] = []
        if score >= 0.8:
            recs.append(f"✅ Très bonne maîtrise de « {concept} », tu peux passer au chapitre suivant.")
        elif score >= self.config.confidence_threshold:
            recs.append(f"👍 Bonne compréhension de « {concept} », quelques révisions suffiront.")
        else:
            recs.append(f"📌 « {concept} » n'est pas encore maîtrisé, il faut revoir le cours et refaire des exercices.")

        wrong = [d for d in detail if not d.get("is_correct", True)]
        if len(wrong) >= 2:
            recs.append("💡 Plusieurs erreurs répétées détectées : reprends la méthode étape par étape avant de continuer.")

        return recs

    def summarize_class_performance(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Agrège les résultats de plusieurs élèves pour l'espace enseignant
        (taux de réussite, chapitres faibles fréquents)."""
        if not results:
            return {"average_score": 0.0, "weak_chapters": []}

        avg = sum(r.get("score", 0.0) for r in results) / len(results)

        chapitre_scores: Dict[str, List[float]] = {}
        for r in results:
            chapitre = r.get("chapitre") or r.get("concept", "inconnu")
            chapitre_scores.setdefault(chapitre, []).append(r.get("score", 0.0))

        weak_chapters = sorted(
            (
                {"chapitre": ch, "average_score": round(sum(scores) / len(scores), 2)}
                for ch, scores in chapitre_scores.items()
            ),
            key=lambda x: x["average_score"],
        )

        return {
            "average_score": round(avg, 2),
            "weak_chapters": [c for c in weak_chapters if c["average_score"] < 0.6],
            "all_chapters": weak_chapters,
        }
