# backend/app/agents/progression_agent.py
"""
Agent Progression - gère l'historique, le score de maîtrise et propose un
parcours d'apprentissage personnalisé (mastery learning).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .config import AgentConfig

logger = logging.getLogger(__name__)


class ProgressionAgent:
    """Suit la progression de l'élève et personnalise le parcours."""

    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()

    def _memory(self):
        """Import paresseux pour éviter une dépendance dure si la DB n'est
        pas configurée (ex: tests unitaires sans DB)."""
        try:
            from backend.app.memory import student_profile

            student_profile.ensure_initialized()
            return student_profile
        except Exception as exc:  # noqa: BLE001
            logger.warning("⚠️ Mémoire élève indisponible: %s", exc)
            return None

    def record_result(
        self,
        student_id: Optional[str],
        concept: Optional[str],
        is_correct: Optional[bool] = None,
        score: Optional[float] = None,
        exercise_type: str = "exercice",
        chapitre: Optional[str] = None,
    ) -> None:
        if not student_id:
            return
        memory = self._memory()
        if memory is None:
            return
        try:
            memory.record_exercise_result(
                student_id=student_id,
                concept=concept,
                is_correct=is_correct,
                score=score,
                exercise_type=exercise_type,
                chapitre=chapitre,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("❌ Erreur enregistrement progression: %s", exc)

    def log_interaction(
        self,
        student_id: Optional[str],
        user_message: str,
        intent: str,
        level: str,
        concept: Optional[str],
        response: str,
        session_id: Optional[str] = None,
    ) -> None:
        if not student_id:
            return
        memory = self._memory()
        if memory is None:
            return
        try:
            memory.log_interaction(
                student_id=student_id,
                user_message=user_message,
                intent=intent,
                level=level,
                concept=concept,
                response=response,
                session_id=session_id,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("❌ Erreur enregistrement interaction: %s", exc)

    def get_profile_summary(self, student_id: Optional[str]) -> Dict[str, Any]:
        """Retourne un résumé de progression : notions faibles, historique récent."""
        if not student_id:
            return {"mastery": [], "weak_concepts": [], "recent_interactions": []}

        memory = self._memory()
        if memory is None:
            return {"mastery": [], "weak_concepts": [], "recent_interactions": []}

        try:
            return {
                "mastery": memory.get_mastery_map(student_id),
                "weak_concepts": memory.get_weak_concepts(student_id),
                "recent_interactions": memory.get_recent_interactions(student_id, limit=5),
            }
        except Exception as exc:  # noqa: BLE001
            logger.error("❌ Erreur lecture progression: %s", exc)
            return {"mastery": [], "weak_concepts": [], "recent_interactions": []}

    def suggest_next_step(self, student_id: Optional[str], current_concept: Optional[str] = None) -> Dict[str, Any]:
        """Propose la prochaine action pédagogique (mastery learning) :
        - si le concept courant est faible -> proposer de le retravailler ;
        - sinon -> proposer la notion la plus faible du profil, ou avancer.
        """
        summary = self.get_profile_summary(student_id)
        weak_concepts = summary.get("weak_concepts", [])

        if weak_concepts:
            target = weak_concepts[0]
            return {
                "action": "revision",
                "concept": target["concept"],
                "chapitre": target.get("chapitre"),
                "reason": f"Notion pas encore maîtrisée (score {target['mastery_score']}).",
            }

        return {
            "action": "avancer",
            "concept": current_concept,
            "reason": "Les notions travaillées jusqu'ici sont bien maîtrisées, tu peux avancer dans le programme.",
        }

    def get_badges(self, student_id: Optional[str]) -> list:
        if not student_id:
            return []
        memory = self._memory()
        if memory is None:
            return []
        try:
            return memory.get_badges(student_id)
        except Exception as exc:  # noqa: BLE001
            logger.error("❌ Erreur lecture badges: %s", exc)
            return []

    def get_competency_map(self, student_id: Optional[str]) -> Dict[str, Any]:
        """Construit la carte des compétences à partir des notions
        effectivement travaillées et enregistrées dans la mémoire élève."""
        mastery_map = {m["concept"]: m for m in self.get_profile_summary(student_id).get("mastery", [])}

        nodes = [
            {
                "chapitre": m.get("chapitre"),
                "concept": m["concept"],
                "mastery_score": m["mastery_score"],
                "attempts": m["attempts"],
                "status": self._mastery_status(m["mastery_score"]),
            }
            for m in mastery_map.values()
        ]

        return {"nodes": nodes}

    @staticmethod
    def _mastery_status(score: float) -> str:
        if score >= 0.8:
            return "maitrise"
        if score >= 0.5:
            return "en_cours"
        if score > 0:
            return "faible"
        return "non_commence"
