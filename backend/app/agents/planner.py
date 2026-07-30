# backend/app/agents/planner.py
"""
Agent Planificateur - analyse la demande de l'élève et détermine :
1. l'intention (cours, exercice, quiz, calcul, général) ;
2. le niveau d'aide (reformulation -> rappel -> indice -> solution guidée -> complète) ;
3. les agents et outils nécessaires ;
4. les paramètres (concept, difficulté, type de quiz...).

Implémentation basée sur des règles/mots-clés (rapide, déterministe, sans
coût LLM) : suffisant car il s'agit d'un routage, pas d'une génération de
contenu pédagogique.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, Optional

from .config import AgentConfig
from .state import AgentState
from ..tools.math_tools import detect_math_intent

logger = logging.getLogger(__name__)

_COURS_KEYWORDS = ["explique", "explication", "résume", "resume", "qu'est-ce que", "c'est quoi", "cours sur", "rappelle", "définis", "definis"]
_EXERCICE_KEYWORDS = ["exercice", "problème", "probleme", "entraîne", "entraine", "exerce"]
_QUIZ_KEYWORDS = ["quiz", "qcm", "teste", "vrai ou faux", "vrai/faux", "évalue-moi", "evalue-moi"]
_CALCUL_KEYWORDS = ["dérive", "derive", "intégra", "integra", "résous", "resous", "calcule", "simplifie", "factorise", "développe", "developpe"]

_HELP_LEVEL_HINTS = {
    "solution_complete": ["donne-moi la solution", "réponse complète", "reponse complete", "corrige tout", "correction complète", "correction complete"],
    "solution_guidee": ["aide-moi à résoudre", "aide moi a resoudre", "comment faire"],
    "indice": ["indice", "aide-moi un peu", "un indice"],
    "rappel": ["rappelle-moi", "rappel"],
}


def _extract_concept(message: str) -> str:
    """Extraction naïve du concept mathématique visé, en retirant les mots
    déclencheurs les plus courants. Suffisant pour router le RAG ; le
    retriever fait ensuite une recherche sémantique, pas exacte."""
    text = message.strip()
    text = re.sub(
        r"(?i)\b(explique[-\s]?moi|explication de|résume|resume|fais[-\s]?moi|donne[-\s]?moi|"
        r"génère[-\s]?moi|genere[-\s]?moi|crée[-\s]?moi|cree[-\s]?moi|créer?|creer?|"
        r"je veux réviser|je veux reviser|je veux revoir|"
        r"un exercice sur|un quiz sur|un cours sur|le chapitre|sur|"
        r"le|la|les|un|une|des|de|du)\b",
        " ",
        text,
    )
    text = re.sub(r"\s+", " ", text).strip(" ?!.")
    return text or message.strip()


class PlannerAgent:
    """Détermine le plan d'exécution (intention, niveau, agents, outils)."""

    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()

    def plan(self, state: AgentState) -> Dict[str, Any]:
        message = state.user_message
        text = message.lower()

        intent = self._detect_intent(text)
        level = self._detect_level(text, state)
        concept = _extract_concept(message)
        math_intent = detect_math_intent(message)

        required_agents = ["retriever"]
        required_tools = []

        if intent == "cours":
            required_agents.append("cours")
        elif intent == "exercice":
            required_agents.append("exercices")
        elif intent == "quiz":
            required_agents.append("quiz")
        else:
            required_agents.append("cours")  # repli conversationnel par défaut

        if math_intent:
            required_tools.append(math_intent["tool"])

        required_agents.append("verifier")

        parameters = {
            "concept": concept,
            "difficulty": self._detect_difficulty(text),
            "quiz_type": self._detect_quiz_type(text),
        }
        if math_intent:
            parameters["math_tool"] = math_intent["tool"]
            # `detect_math_intent` garantit deja qu'une expression exploitable
            # a ete trouvee (voir math_tools.py) : ne jamais retomber sur le
            # concept en langage naturel, qui n'est pas une expression valide
            # et produirait un calcul SymPy absurde (ex: derivee de "dérivées").
            parameters["math_expression"] = math_intent["expression"]

        plan = {
            "intent": intent,
            "level": level,
            "required_agents": required_agents,
            "required_tools": required_tools,
            "parameters": parameters,
        }
        logger.debug("Plan généré: %s", plan)
        return plan

    def _detect_intent(self, text: str) -> str:
        if any(k in text for k in _QUIZ_KEYWORDS):
            return "quiz"
        if any(k in text for k in _EXERCICE_KEYWORDS):
            return "exercice"
        if any(k in text for k in _CALCUL_KEYWORDS):
            return "cours"  # un calcul s'accompagne toujours d'une explication pédagogique
        if any(k in text for k in _COURS_KEYWORDS):
            return "cours"
        return "general"

    def _detect_level(self, text: str, state: AgentState) -> str:
        for level, hints in _HELP_LEVEL_HINTS.items():
            if any(h in text for h in hints):
                return level

        # Escalade progressive : si l'élève revient plusieurs fois sur le
        # même échange (itérations), on augmente le niveau d'aide.
        if state.iterations >= 3:
            return "solution_guidee"
        if state.iterations >= 1:
            return "indice"
        return "reformulation"

    def _detect_difficulty(self, text: str) -> str:
        if any(k in text for k in ["facile", "simple", "débutant", "debutant"]):
            return "easy"
        if any(k in text for k in ["difficile", "avancé", "avance", "bac", "examen"]):
            return "hard"
        return "intermediate"

    def _detect_quiz_type(self, text: str) -> str:
        if "vrai" in text and "faux" in text:
            return "vrai_faux"
        if "qcm" in text:
            return "qcm"
        if "question ouverte" in text or "questions ouvertes" in text:
            return "questions"
        return "qcm"
