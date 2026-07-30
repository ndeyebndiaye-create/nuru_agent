# backend/agents/quiz_agent.py
"""
Agent Quiz - Génère des questions d'évaluation via le LLM local, avec un
format JSON structuré validé (jamais de contenu placeholder affiché).
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

from .config import AgentConfig
from .llm_utils import generate_pedagogical_text

logger = logging.getLogger(__name__)

# Signatures des anciens gabarits statiques : si l'une de ces chaînes apparaît
# dans un quiz (généré par le LLM ou par un repli), il n'est jamais affiché
# tel quel à l'élève — on régénère ou on renvoie une liste vide.
_PLACEHOLDER_MARKERS = (
    "définition correcte",
    "definition correcte",
    "définition incorrecte",
    "definition incorrecte",
    "application 1",
    "application 2",
    "application 3",
    "application 4",
    "option 1",
    "option 2",
    "placeholder",
)

_MAX_ATTEMPTS = 2


def _contains_placeholder(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in _PLACEHOLDER_MARKERS)


def _build_consistent_explanation(
    correct_answer: Any,
    choices: List[Dict[str, Any]],
    generated_explanation: Any,
) -> str:
    """Ancre l'explication sur l'option désignée par correct_answer.

    Le LLM peut produire un JSON structurellement valide tout en justifiant
    une autre proposition que celle indiquée par correct_answer. La phrase
    canonique garantit que la correction affichée désigne toujours le même
    identifiant et le même texte que l'évaluation. L'explication libre du
    LLM n'est conservée que si elle mentionne le texte de l'option correcte
    sans mentionner celui d'une autre option.
    """
    correct_choice = next(choice for choice in choices if choice["id"] == correct_answer)
    correct_text = str(correct_choice["text"]).strip()
    canonical = f"La bonne réponse est {correct_answer} : {correct_text}."

    generated = str(generated_explanation or "").strip()
    if not generated:
        return canonical

    generated_norm = generated.casefold()
    correct_norm = correct_text.casefold()
    mentions_correct = bool(correct_norm and correct_norm in generated_norm)
    mentions_other = any(
        (other_text := str(choice["text"]).strip().casefold())
        and other_text in generated_norm
        for choice in choices
        if choice["id"] != correct_answer
    )

    if mentions_correct and not mentions_other:
        return f"{canonical} {generated}"
    return canonical


class QuizAgent:
    """
    Agent spécialisé dans les quiz, appuyé sur le LLM pour le QCM et le
    Vrai/Faux (jamais de gabarit statique affiché à l'élève).
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()

    def generate(self, state: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère un quiz.

        Args:
            state: État actuel
            context: Contexte (concept, quiz_type, prompt_context)

        Returns:
            Quiz structuré. `questions` est une liste vide si le LLM n'a pas
            réussi à produire un quiz valide après plusieurs tentatives —
            jamais remplie de contenu placeholder de repli.
        """
        concept = context.get("concept", "le concept")
        quiz_type = context.get("quiz_type", "qcm")
        prompt_context = context.get("prompt_context", "")

        if quiz_type == "questions":
            quiz = self._generate_questions(concept)
        else:
            quiz = self._generate_llm_quiz(concept, quiz_type, prompt_context)

        return {
            "type": "quiz",
            "quiz_type": quiz_type,
            "concept": concept,
            "questions": quiz,
            "instructions": (
                f"Réponds aux questions sur {concept}."
                if quiz
                else "⚠️ Le quiz n'a pas pu être généré correctement pour le moment. Réessaie dans un instant."
            ),
        }

    # ------------------------------------------------------------- LLM (QCM / Vrai-Faux)

    def _generate_llm_quiz(self, concept: str, quiz_type: str, prompt_context: str) -> List[Dict[str, Any]]:
        """Demande au LLM une question de quiz au format JSON structuré.

        Ne renvoie jamais de contenu placeholder : si le LLM échoue à
        produire un JSON valide et sans placeholder après `_MAX_ATTEMPTS`
        tentatives, retourne une liste vide plutôt qu'un gabarit factice.
        """
        if quiz_type == "vrai_faux":
            schema_hint = (
                'Exactement 2 propositions : {"id": "A", "text": "Vrai"} et {"id": "B", "text": "Faux"}.'
            )
        else:
            schema_hint = "Exactement 4 propositions distinctes, une seule correcte."

        prompt = (
            f"Tu es Gemini, un modèle expert en mathématiques. Génère UNE SEULE question de quiz de type {quiz_type} "
            f"sur le thème « {concept} », de niveau Terminale S1 (programme sénégalais).\n"
            "Tu es libre d'utiliser tes propres connaissances internes pour concevoir ce quiz (pas besoin de te limiter au contexte strict).\n"
            "Utilise la syntaxe MathJax / KaTeX ($, $$) pour les formules mathématiques dans le texte de la question et les choix.\n"
            "Réponds STRICTEMENT avec un unique objet JSON, sans aucun texte avant ou après, "
            "sans balise markdown, au format exact suivant :\n"
            '{"question": "...", "choices": [{"id": "A", "text": "..."}, {"id": "B", "text": "..."}, '
            '{"id": "C", "text": "..."}, {"id": "D", "text": "..."}], "correct_answer": "A", "explanation": "..."}\n'
            f"{schema_hint} Les propositions doivent être des affirmations mathématiques réelles et "
            "distinctes en lien avec le concept — jamais de texte générique comme \"Option 1\" ou "
            "\"Définition incorrecte 1\". La valeur de correct_answer doit désigner exactement "
            "la proposition justifiée par explanation ; explanation ne doit justifier aucune autre option."
        )

        for attempt in range(1, _MAX_ATTEMPTS + 1):
            raw = generate_pedagogical_text(prompt, prompt_context)
            parsed = self._parse_quiz_json(raw)
            if parsed is not None and not _contains_placeholder(json.dumps(parsed, ensure_ascii=False)):
                return [parsed]
            logger.warning(
                "⚠️ Quiz LLM invalide ou avec placeholder (tentative %d/%d) pour « %s » : %r",
                attempt, _MAX_ATTEMPTS, concept, (raw or "")[:200],
            )

        return []

    def _parse_quiz_json(self, raw: str) -> Optional[Dict[str, Any]]:
        """Extrait et valide un objet JSON de quiz depuis la réponse brute du LLM.

        Le LLM peut entourer le JSON de texte libre ou de balises markdown
        (```json ... ```) : on extrait le premier bloc `{...}` rencontré.
        """
        if not raw:
            return None

        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return None

        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

        if not isinstance(data, dict):
            return None

        question = data.get("question")
        choices = data.get("choices")
        correct_answer = data.get("correct_answer")

        if not question or not isinstance(choices, list) or len(choices) < 2:
            return None
        if not all(isinstance(c, dict) and c.get("id") and c.get("text") for c in choices):
            return None

        valid_ids = {c["id"] for c in choices}
        if correct_answer not in valid_ids:
            return None

        return {
            "question": question,
            "choices": choices,
            "correct_answer": correct_answer,
            "explanation": _build_consistent_explanation(
                correct_answer,
                choices,
                data.get("explanation"),
            ),
        }

    # ------------------------------------------------------------- Questions ouvertes

    def _generate_questions(self, concept: str) -> List[Dict[str, Any]]:
        """Génère des questions ouvertes (pas de choix à valider, donc pas de
        risque de placeholder de type QCM)."""
        return [
            {
                "question": f"Définis {concept} en tes propres mots.",
                "type": "open",
            },
            {
                "question": f"Explique l'importance de {concept}.",
                "type": "open",
            },
        ]
