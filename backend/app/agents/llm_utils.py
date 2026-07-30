# backend/app/agents/llm_utils.py
"""
Accès partagé (singleton) au client LLM local, utilisé par les agents
pédagogiques pour générer du texte à partir du contexte RAG.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

_llm_client = None


def get_llm():
    """Retourne le client LLM (Ollama local), en le créant si nécessaire.

    Ne lève jamais d'exception : si Ollama est indisponible, le client
    retourne lui-même des réponses de secours (voir OllamaClient._fallback_response).
    """
    global _llm_client
    if _llm_client is None:
        try:
            from backend.app.llm.ollama_client import OllamaClient

            model = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
            _llm_client = OllamaClient(model=model)
        except Exception as exc:  # noqa: BLE001
            logger.error("❌ Impossible d'initialiser le client LLM: %s", exc)
            _llm_client = None
    return _llm_client


def generate_pedagogical_text(prompt: str, context: str = "", system_prompt: str = "") -> str:
    """Génère du texte pédagogique via le LLM, avec repli si indisponible.
    
    Args:
        prompt:        Instruction / question à envoyer au LLM.
        context:       Contexte RAG à injecter avant le prompt.
        system_prompt: Instruction système personnalisée. Si vide, utilise
                       le système par défaut du client LLM.
    """
    llm = get_llm()
    if llm is None:
        return "⚠️ LLM indisponible pour le moment. Réessaie plus tard."
    return llm.generate(prompt, context, system_prompt=system_prompt)
