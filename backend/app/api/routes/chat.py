# backend/app/api/routes/chat.py
"""
Routes de chat - branchées sur l'orchestrateur LangGraph (agents/graph.py),
la mémoire élève (student_profile) et l'agent Evaluation.
"""
from fastapi import APIRouter, HTTPException, status, Depends
import uuid
from datetime import datetime
import logging
from typing import Any, Dict, Optional

from backend.app.api.models.requests import ChatRequest, FeedbackRequest
from backend.app.api.models.responses import SessionResponse
from backend.app.api.dependencies.containers import get_orchestrator, get_session_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])

# Sessions temporaires (historique conversationnel côté API, en plus de la
# mémoire élève persistante en base de données). Peut aussi contenir
# "active_quiz" : {concept, chapitre, questions, current_index, attempts}
# tant qu'un quiz généré n'a pas été entièrement répondu (voir
# _handle_active_quiz_answer) — évite qu'une réponse ("1", "A"...) soit
# interprétée par le Planner comme une toute nouvelle question générale.
sessions = {}


def _get_student_id(user_id: str | None) -> str | None:
    """Résout un student_id interne à partir du user_id externe (si fourni)."""
    if not user_id:
        return None
    try:
        from backend.app.memory import student_profile

        student_profile.ensure_initialized()
        return student_profile.get_or_create_student(external_user_id=user_id)
    except Exception as exc:  # noqa: BLE001
        logger.warning("⚠️ Mémoire élève indisponible, poursuite sans persistance: %s", exc)
        return None


def _handle_active_quiz_answer(
    session: Dict[str, Any], student_id: Optional[str], session_id: str, message: str
) -> Dict[str, Any]:
    """Interprète le message comme la réponse à la question de quiz en cours
    (état conservé côté session), corrige via `EvaluationAgent`, met à jour
    la progression, puis propose la question suivante ou clôture le quiz.
    """
    from backend.app.agents import EvaluationAgent, ProgressionAgent

    active_quiz = session["active_quiz"]
    questions = active_quiz["questions"]
    current_index = active_quiz["current_index"]
    concept = active_quiz.get("concept", "le concept")
    question = questions[current_index]

    evaluation = EvaluationAgent().evaluate_quiz(concept, [question], [message])
    detail = evaluation["detail"][0]
    is_correct = bool(detail["is_correct"])

    if student_id:
        ProgressionAgent().record_result(
            student_id=student_id,
            concept=concept,
            is_correct=is_correct,
            exercise_type="quiz",
            chapitre=active_quiz.get("chapitre"),
        )

    active_quiz["attempts"] = active_quiz.get("attempts", 0) + 1
    active_quiz["current_index"] += 1
    quiz_finished = active_quiz["current_index"] >= len(questions)

    parts = [
        "✅ Bonne réponse !" if is_correct
        else f"❌ Pas tout à fait. La bonne réponse était **{detail['expected']}**."
    ]
    explanation = question.get("explanation")
    if explanation:
        parts.append(f"💡 {explanation}")

    if quiz_finished:
        del session["active_quiz"]
        parts.append(f"\n🏁 Quiz terminé sur « {concept} ».")
    else:
        next_question = questions[active_quiz["current_index"]]
        parts.append("\n📋 **Question suivante :**")
        parts.append(next_question.get("question", ""))
        for choice in next_question.get("choices", []):
            parts.append(f"   {choice.get('id', '')}. {choice.get('text', '')}")

    progression_summary: Dict[str, Any] = {}
    if student_id:
        progression_summary = ProgressionAgent().get_profile_summary(student_id)

    return {
        "response": "\n".join(p for p in parts if p),
        "intent": "quiz_answer",
        "level": "quiz",
        "confidence": 1.0 if is_correct else 0.5,
        "session_id": session_id,
        "math_tool_result": None,
        "progression_summary": progression_summary,
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/")
async def chat(payload: ChatRequest):
    """Point d'entrée principal du chatbot élève, exécute le graphe LangGraph complet."""
    try:
        session_id = payload.session_id or str(uuid.uuid4())

        if session_id not in sessions:
            sessions[session_id] = {
                "created_at": datetime.now().isoformat(),
                "history": [],
            }

        session = sessions[session_id]
        student_id = _get_student_id(payload.user_id)

        if session.get("active_quiz"):
            result = _handle_active_quiz_answer(session, student_id, session_id, payload.message)
            session["history"].append({
                "user": payload.message,
                "assistant": result["response"],
                "timestamp": result["timestamp"],
            })
            return result

        iterations = len(session["history"])

        orchestrator = get_orchestrator()
        result = orchestrator.process(
            user_message=payload.message,
            context=payload.context,
            student_id=student_id,
            session_id=session_id,
            iterations=iterations,
        )

        # Un quiz vient d'être généré avec au moins une question valide :
        # on mémorise l'état actif pour que le prochain message de l'élève
        # soit traité comme une réponse au quiz (voir _handle_active_quiz_answer)
        # plutôt que comme une nouvelle question générale.
        quiz_response = result.get("responses", {}).get("quiz")
        if quiz_response and quiz_response.get("questions"):
            session["active_quiz"] = {
                "concept": quiz_response.get("concept"),
                "chapitre": None,
                "questions": quiz_response["questions"],
                "current_index": 0,
                "attempts": 0,
            }

        session["history"].append({
            "user": payload.message,
            "assistant": result["response"],
            "timestamp": datetime.now().isoformat(),
        })

        return {
            "response": result["response"],
            "intent": result["intent"],
            "level": result["level"],
            "confidence": result["confidence"],
            "session_id": session_id,
            "math_tool_result": result.get("math_tool_result"),
            "progression_summary": result.get("progression_summary"),
            "timestamp": result["timestamp"],
        }

    except Exception as e:
        logger.error(f"Erreur: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session non trouvée"
        )

    return {
        "session_id": session_id,
        "created_at": sessions[session_id]["created_at"],
        "history_length": len(sessions[session_id]["history"]),
        "history": sessions[session_id]["history"],
    }


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    return {"status": "deleted"}


@router.get("/progression/{user_id}")
async def get_progression(user_id: str):
    """Retourne le profil de progression (maîtrise, notions faibles) d'un élève."""
    student_id = _get_student_id(user_id)
    if not student_id:
        raise HTTPException(status_code=404, detail="Élève introuvable ou mémoire indisponible")

    from backend.app.agents import ProgressionAgent

    progression_agent = ProgressionAgent()
    summary = progression_agent.get_profile_summary(student_id)
    next_step = progression_agent.suggest_next_step(student_id)
    return {"student_id": student_id, **summary, "next_step": next_step}


@router.get("/badges/{user_id}")
async def get_badges(user_id: str):
    """Badges débloqués par l'élève (gamification)."""
    student_id = _get_student_id(user_id)
    if not student_id:
        raise HTTPException(status_code=404, detail="Élève introuvable ou mémoire indisponible")

    from backend.app.agents import ProgressionAgent

    return {"student_id": student_id, "badges": ProgressionAgent().get_badges(student_id)}


@router.get("/competency-map/{user_id}")
async def get_competency_map(user_id: str):
    """Carte des compétences issue de la maîtrise enregistrée de l'élève."""
    student_id = _get_student_id(user_id)
    if not student_id:
        raise HTTPException(status_code=404, detail="Élève introuvable ou mémoire indisponible")

    from backend.app.agents import ProgressionAgent

    progression_agent = ProgressionAgent()
    return {
        "student_id": student_id,
        **progression_agent.get_competency_map(student_id),
    }


@router.post("/feedback")
async def submit_feedback(payload: FeedbackRequest):
    """Enregistre un retour élève sur la réponse (utile pour l'agent Verifier / analytics)."""
    if payload.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    sessions[payload.session_id].setdefault("feedback", []).append(payload.dict())
    return {"status": "recorded"}
