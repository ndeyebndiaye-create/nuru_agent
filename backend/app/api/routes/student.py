# backend/app/api/routes/student.py
"""
Routes de l'espace Élève :
- /student/dashboard/{user_id} : Récupère la progression réelle de l'élève (0% état vide si aucune évaluation)
- /student/generate-quiz      : Génération automatique de quiz sur-mesure par l'Agent IA
- /student/generate-exercise  : Génération d'exercices sur-mesure par l'Agent IA
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/student", tags=["Élève"])


class GenerateQuizRequest(BaseModel):
    concept: str = Field(..., description="Concept ou chapitre visé, ex: Logarithme Néperien")
    num_questions: int = Field(3, ge=1, le=10)
    difficulty: str = "intermediate"


class GenerateExerciseRequest(BaseModel):
    concept: str = Field(..., description="Concept ou chapitre visé, ex: Dérivation")
    difficulty: str = "intermediate"


def _ensure_memory():
    from backend.app.memory import student_profile, auth_service
    student_profile.ensure_initialized()
    auth_service.ensure_super_admin()


def _resolve_student_id(user_id: str) -> Optional[str]:
    from backend.app.memory import student_profile, auth_service
    with auth_service.get_session() as session:
        from backend.app.memory.models import Student, User
        st = session.query(Student).filter_by(id=user_id).first()
        if st:
            return st.id
        st = session.query(Student).filter_by(external_user_id=user_id).first()
        if st:
            return st.id
        u = session.query(User).filter_by(email=user_id).first()
        if u and u.role == "student":
            st = session.query(Student).filter_by(external_user_id=u.id).first()
            if st:
                return st.id
    return student_profile.get_or_create_student(external_user_id=user_id)


@router.get("/dashboard/{user_id}")
async def get_student_dashboard(user_id: str):
    _ensure_memory()
    from backend.app.memory import student_profile
    from backend.app.memory.auth_service import get_student_recommendations

    student_id = _resolve_student_id(user_id)
    if not student_id:
        raise HTTPException(status_code=404, detail="Élève non trouvé")

    mastery_map = student_profile.get_mastery_map(student_id)
    badges = student_profile.get_badges(student_id)
    recent_interactions = student_profile.get_recent_interactions(student_id, limit=5)
    recommendations = get_student_recommendations(student_id)

    # Récupération des résultats réels d'exercices
    from backend.app.memory.db import get_session
    from backend.app.memory.models import ExerciseResult
    with get_session() as session:
        results = session.query(ExerciseResult).filter_by(student_id=student_id).all()
        nb_evaluations = len(results)
        total_xp = sum(20 for r in results if r.is_correct or (r.score and r.score >= 0.5))

        history = [
            {
                "id": r.id,
                "concept": r.concept,
                "chapitre": r.chapitre,
                "exercise_type": r.exercise_type,
                "score": round((r.score or 0) * 100, 1) if r.score is not None else (100 if r.is_correct else 0),
                "is_correct": r.is_correct,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in reversed(results[-10:])
        ]

    overall_mastery = round(sum(m["mastery_score"] for m in mastery_map) / len(mastery_map) * 100, 1) if mastery_map else 0.0

    return {
        "student_id": student_id,
        "nb_evaluations": nb_evaluations,
        "total_xp": total_xp,
        "overall_mastery": overall_mastery,
        "mastery_map": mastery_map,
        "badges": badges,
        "history": history,
        "recent_interactions": recent_interactions,
        "recommendations": recommendations,
        "is_empty_state": (nb_evaluations == 0),
    }


@router.post("/generate-quiz")
async def generate_quiz(payload: GenerateQuizRequest):
    """Auto-génération de quiz sur mesure par l'Agent Quiz + Retriever."""
    from backend.app.agents import QuizAgent, RetrieverAgent, AgentConfig
    from backend.app.api.dependencies.containers import get_retriever

    config = AgentConfig()
    retriever_agent = RetrieverAgent(config, retriever=get_retriever())
    retrieval = retriever_agent.retrieve(query=payload.concept, concept=payload.concept, top_k=5)
    prompt_context = retriever_agent.build_prompt_context(retrieval)

    quiz_agent = QuizAgent(config)
    res = quiz_agent.generate(
        concept=payload.concept,
        difficulty=payload.difficulty,
        prompt_context=prompt_context,
        num_questions=payload.num_questions,
    )
    return res


@router.post("/generate-exercise")
async def generate_exercise(payload: GenerateExerciseRequest):
    """Auto-génération d'exercice sur mesure par l'Agent Exercices + Retriever."""
    from backend.app.agents import ExercicesAgent, RetrieverAgent, AgentConfig
    from backend.app.api.dependencies.containers import get_retriever

    config = AgentConfig()
    retriever_agent = RetrieverAgent(config, retriever=get_retriever())
    retrieval = retriever_agent.retrieve(query=payload.concept, concept=payload.concept, top_k=5)
    prompt_context = retriever_agent.build_prompt_context(retrieval)

    exercices_agent = ExercicesAgent(config)
    res = exercices_agent.generate(
        concept=payload.concept,
        difficulty=payload.difficulty,
        prompt_context=prompt_context,
    )
    return res
