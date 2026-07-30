# backend/app/api/routes/teacher.py
"""
Routes de l'espace Enseignant : suivi connecté des élèves, liaison,
recommandation d'exercices ciblés, et génération pédagogique RAG.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/teacher", tags=["Enseignant"])


class TeacherRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: Optional[str] = None


class TeacherLoginRequest(BaseModel):
    email: EmailStr
    password: str


class LinkStudentRequest(BaseModel):
    teacher_id: str
    student_external_id: str


class TeacherCourseRequest(BaseModel):
    concept: str
    chapitre: Optional[str] = None


class RecommendExerciseRequest(BaseModel):
    teacher_id: str
    student_id: str
    concept: str
    chapitre: Optional[str] = None
    message: Optional[str] = None


def _ensure_memory():
    from backend.app.memory import student_profile, auth_service
    student_profile.ensure_initialized()
    auth_service.ensure_super_admin()


@router.post("/register")
async def register_teacher(payload: TeacherRegisterRequest):
    _ensure_memory()
    from backend.app.memory.auth_service import register_user, AuthError

    try:
        return register_user(
            email=payload.email,
            password=payload.password,
            role="teacher",
            name=payload.name or payload.email.split("@")[0],
        )
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/login")
async def login_teacher(payload: TeacherLoginRequest):
    _ensure_memory()
    from backend.app.memory.auth_service import authenticate_user, AuthError

    try:
        return authenticate_user(payload.email, payload.password)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc))


@router.post("/link-student")
async def link_student(payload: LinkStudentRequest):
    _ensure_memory()
    from backend.app.memory.auth_service import link_student_public, AuthError

    try:
        return link_student_public(payload.teacher_id, "teacher", payload.student_external_id)
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/students/{teacher_id}")
async def list_students(teacher_id: str):
    _ensure_memory()
    from backend.app.memory.auth_service import get_teacher_students_data

    students = get_teacher_students_data(teacher_id)
    return {"teacher_id": teacher_id, "students": students}


@router.post("/recommend-exercise")
async def recommend_exercise(payload: RecommendExerciseRequest):
    _ensure_memory()
    from backend.app.memory.auth_service import add_recommendation

    return add_recommendation(
        teacher_id=payload.teacher_id,
        student_id=payload.student_id,
        concept=payload.concept,
        chapitre=payload.chapitre,
        message=payload.message,
    )


@router.get("/class-stats/{teacher_id}")
async def class_stats(teacher_id: str):
    """Statistiques agrégées : progression, erreurs fréquentes, taux de
    réussite des élèves suivis par cet enseignant."""
    _ensure_memory()
    from backend.app.memory.auth_service import get_teacher_students_data
    from backend.app.agents import EvaluationAgent

    students = get_teacher_students_data(teacher_id)

    all_results = []
    for s in students:
        for m in s.get("mastery_map", []):
            all_results.append({
                "concept": m["concept"],
                "chapitre": m.get("chapitre"),
                "score": m["mastery_score"],
            })

    evaluation_agent = EvaluationAgent()
    class_summary = evaluation_agent.summarize_class_performance(all_results)

    return {
        "teacher_id": teacher_id,
        "nb_students": len(students),
        "class_summary": class_summary,
        "students": students,
    }


@router.post("/generate-course")
async def generate_course(payload: TeacherCourseRequest):
    """Génère un cours complet à partir du corpus RAG (Agent Cours + Retriever),
    destiné à l'enseignant pour préparer sa classe."""
    from backend.app.agents import CoursAgent, RetrieverAgent, AgentConfig
    from backend.app.agents.state import AgentState
    from backend.app.api.dependencies.containers import get_retriever

    config = AgentConfig()
    retriever_agent = RetrieverAgent(config, retriever=get_retriever())
    retrieval = retriever_agent.retrieve(query=payload.concept, concept=payload.concept, top_k=8)
    prompt_context = retriever_agent.build_prompt_context(retrieval, max_chars=4000)

    cours_agent = CoursAgent(config)
    state = AgentState(user_message=f"Cours complet sur {payload.concept}")
    state.current_level = "solution_complete"
    response = cours_agent.explain(state, {
        "concept": payload.concept,
        "retrieved_docs": retrieval["documents"],
        "prompt_context": prompt_context,
    })
    return response
