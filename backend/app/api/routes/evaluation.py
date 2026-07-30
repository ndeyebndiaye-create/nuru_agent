# backend/app/api/routes/evaluation.py
"""
Routes d'évaluation - corrige un quiz/exercice via l'agent Evaluation et
met à jour la maîtrise de l'élève via l'agent Progression.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


class QuizCorrectionRequest(BaseModel):
    user_id: Optional[str] = None
    concept: str
    chapitre: Optional[str] = None
    questions: List[Dict[str, Any]] = Field(..., description="Questions telles que générées par l'Agent Quiz")
    student_answers: List[Any] = Field(..., description="Réponses de l'élève, dans le même ordre")


class ExerciseCorrectionRequest(BaseModel):
    user_id: Optional[str] = None
    concept: str
    chapitre: Optional[str] = None
    is_correct: bool
    student_answer: Optional[str] = None
    expected_answer: Optional[str] = None
    error_type: Optional[str] = None


def _resolve_student_id(user_id: Optional[str]) -> Optional[str]:
    if not user_id:
        return None
    try:
        from backend.app.memory import student_profile

        student_profile.ensure_initialized()
        return student_profile.get_or_create_student(external_user_id=user_id)
    except Exception as exc:  # noqa: BLE001
        logger.warning("⚠️ Mémoire élève indisponible: %s", exc)
        return None


@router.post("/quiz")
async def correct_quiz(payload: QuizCorrectionRequest):
    from backend.app.agents import EvaluationAgent, ProgressionAgent

    evaluation_agent = EvaluationAgent()
    result = evaluation_agent.evaluate_quiz(payload.concept, payload.questions, payload.student_answers)

    student_id = _resolve_student_id(payload.user_id)
    if student_id:
        progression_agent = ProgressionAgent()
        progression_agent.record_result(
            student_id=student_id,
            concept=payload.concept,
            score=result["score"],
            exercise_type="quiz",
            chapitre=payload.chapitre,
        )

    return result


@router.post("/exercice")
async def correct_exercise(payload: ExerciseCorrectionRequest):
    from backend.app.agents import EvaluationAgent, ProgressionAgent

    evaluation_agent = EvaluationAgent()
    result = evaluation_agent.evaluate_exercise(
        concept=payload.concept,
        is_correct=payload.is_correct,
        student_answer=payload.student_answer,
        expected_answer=payload.expected_answer,
        error_type=payload.error_type,
    )

    student_id = _resolve_student_id(payload.user_id)
    if student_id:
        progression_agent = ProgressionAgent()
        progression_agent.record_result(
            student_id=student_id,
            concept=payload.concept,
            is_correct=payload.is_correct,
            exercise_type="exercice",
            chapitre=payload.chapitre,
        )

    return result
