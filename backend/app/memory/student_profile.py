# backend/app/memory/student_profile.py
"""
Couche d'accès simple (CRUD) à la mémoire élève, utilisée par les agents
Progression et Evaluation ainsi que par l'API.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .db import get_session, init_db
from .models import Student, Interaction, ExerciseResult, ConceptMastery, Badge

logger = logging.getLogger(__name__)

_MASTERY_LEARNING_RATE = 0.3  # pondération de la nouvelle observation


def ensure_initialized() -> None:
    try:
        init_db()
    except Exception as exc:  # noqa: BLE001
        logger.error("❌ Impossible d'initialiser la base mémoire élève: %s", exc)


def get_or_create_student(external_user_id: Optional[str], classe: str = "Terminale", serie: str = "S1") -> str:
    """Retourne l'id interne de l'élève, en le créant si besoin.

    Si external_user_id est None (utilisateur anonyme), un profil éphémère
    est quand même créé pour permettre le suivi de la session en cours.
    """
    with get_session() as session:
        student = None
        if external_user_id:
            student = session.query(Student).filter_by(external_user_id=external_user_id).first()
        if student is None:
            student = Student(external_user_id=external_user_id, classe=classe, serie=serie)
            session.add(student)
            session.flush()
        return student.id


def log_interaction(
    student_id: str,
    user_message: str,
    intent: str,
    level: str,
    concept: Optional[str],
    response: str,
    session_id: Optional[str] = None,
) -> None:
    with get_session() as session:
        session.add(
            Interaction(
                student_id=student_id,
                session_id=session_id,
                user_message=user_message,
                intent=intent,
                level=level,
                concept=concept,
                response=response,
            )
        )


def record_exercise_result(
    student_id: str,
    concept: Optional[str],
    is_correct: Optional[bool] = None,
    score: Optional[float] = None,
    exercise_type: str = "exercice",
    chapitre: Optional[str] = None,
    difficulty: str = "intermediate",
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """Enregistre un résultat d'exercice/quiz et met à jour la maîtrise du concept."""
    with get_session() as session:
        session.add(
            ExerciseResult(
                student_id=student_id,
                concept=concept,
                chapitre=chapitre,
                exercise_type=exercise_type,
                difficulty=difficulty,
                is_correct=is_correct,
                score=score,
                details=details or {},
            )
        )

        if concept:
            mastery = (
                session.query(ConceptMastery)
                .filter_by(student_id=student_id, concept=concept)
                .first()
            )
            observed = score if score is not None else (1.0 if is_correct else 0.0)
            if mastery is None:
                mastery = ConceptMastery(
                    student_id=student_id,
                    concept=concept,
                    chapitre=chapitre,
                    mastery_score=observed,
                    attempts=1,
                    successes=1 if observed >= 0.5 else 0,
                )
                session.add(mastery)
            else:
                # Moyenne mobile exponentielle : la maîtrise évolue
                # progressivement plutôt que de sauter brutalement (mastery
                # learning, comme demandé dans le cahier des charges).
                mastery.mastery_score = (
                    (1 - _MASTERY_LEARNING_RATE) * mastery.mastery_score
                    + _MASTERY_LEARNING_RATE * observed
                )
                mastery.attempts += 1
                mastery.successes += 1 if observed >= 0.5 else 0
                mastery.last_seen = datetime.utcnow()

        _check_and_award_badges(session, student_id, concept, observed)


_BADGE_DEFINITIONS = {
    "premier_pas": {"label": "🌱 Premier pas", "description": "Premier exercice ou quiz complété."},
    "dix_exercices": {"label": "🔥 Persévérant·e", "description": "10 exercices/quiz complétés."},
    "cinquante_exercices": {"label": "🏆 Marathonien·ne", "description": "50 exercices/quiz complétés."},
    "notion_maitrisee": {"label": "✅ Notion maîtrisée", "description": "Une notion atteint 80% de maîtrise."},
    "sans_faute": {"label": "🎯 Sans-faute", "description": "Score parfait (100%) sur un quiz."},
}


def _award_badge_if_new(session, student_id: str, code: str) -> bool:
    existing = session.query(Badge).filter_by(student_id=student_id, code=code).first()
    if existing:
        return False
    definition = _BADGE_DEFINITIONS[code]
    session.add(Badge(student_id=student_id, code=code, label=definition["label"], description=definition["description"]))
    return True


def _check_and_award_badges(session, student_id: str, concept: Optional[str], observed_score: float) -> None:
    """Vérifie les critères de badges simples après un résultat d'exercice/quiz."""
    total_results = session.query(ExerciseResult).filter_by(student_id=student_id).count()

    if total_results >= 1:
        _award_badge_if_new(session, student_id, "premier_pas")
    if total_results >= 10:
        _award_badge_if_new(session, student_id, "dix_exercices")
    if total_results >= 50:
        _award_badge_if_new(session, student_id, "cinquante_exercices")
    if observed_score >= 1.0:
        _award_badge_if_new(session, student_id, "sans_faute")
    if concept:
        mastery = session.query(ConceptMastery).filter_by(student_id=student_id, concept=concept).first()
        if mastery and mastery.mastery_score >= 0.8:
            _award_badge_if_new(session, student_id, "notion_maitrisee")


def get_badges(student_id: str) -> List[Dict[str, Any]]:
    with get_session() as session:
        rows = session.query(Badge).filter_by(student_id=student_id).order_by(Badge.earned_at.desc()).all()
        return [
            {"code": r.code, "label": r.label, "description": r.description, "earned_at": r.earned_at.isoformat() if r.earned_at else None}
            for r in rows
        ]


def get_mastery_map(student_id: str) -> List[Dict[str, Any]]:
    """Retourne la carte de maîtrise de l'élève, triée des notions les plus
    faibles aux plus fortes (utile pour prioriser les révisions)."""
    with get_session() as session:
        rows = (
            session.query(ConceptMastery)
            .filter_by(student_id=student_id)
            .order_by(ConceptMastery.mastery_score.asc())
            .all()
        )
        return [
            {
                "concept": r.concept,
                "chapitre": r.chapitre,
                "mastery_score": round(r.mastery_score, 2),
                "attempts": r.attempts,
                "successes": r.successes,
                "last_seen": r.last_seen.isoformat() if r.last_seen else None,
            }
            for r in rows
        ]


def get_weak_concepts(student_id: str, threshold: float = 0.5, limit: int = 5) -> List[Dict[str, Any]]:
    mastery = get_mastery_map(student_id)
    weak = [m for m in mastery if m["mastery_score"] < threshold]
    return weak[:limit]


def get_recent_interactions(student_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    with get_session() as session:
        rows = (
            session.query(Interaction)
            .filter_by(student_id=student_id)
            .order_by(Interaction.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "user_message": r.user_message,
                "intent": r.intent,
                "level": r.level,
                "concept": r.concept,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]
