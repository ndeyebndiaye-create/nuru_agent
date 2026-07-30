# backend/app/agents/orchestrator.py
"""
Agent Orchestrateur - point d'entrée unique pour le chatbot NURU.

Depuis la migration vers LangGraph, cette classe est un wrapper fin autour
de `NuruGraph` (backend.app.agents.graph). Elle est conservée pour ne pas
casser le code appelant existant (containers.py, tests) qui instancie
`OrchestratorAgent` et appelle `.process(message)`.
"""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from .config import AgentConfig
from .graph import NuruGraph

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """
    Orchestrateur principal, basé sur le graphe LangGraph NuruGraph.
    """

    def __init__(self, config: Optional[AgentConfig] = None, retriever=None):
        self.config = config or AgentConfig()
        self._graph = NuruGraph(self.config, retriever=retriever)

    def process(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None,
        student_id: Optional[str] = None,
        session_id: Optional[str] = None,
        iterations: int = 0,
    ) -> Dict[str, Any]:
        """
        Traite la demande de l'utilisateur en exécutant le graphe LangGraph.

        Args:
            user_message: Message de l'utilisateur
            context: Contexte supplémentaire
            student_id: identifiant interne élève (mémoire/progression)
            session_id: identifiant de session (regroupe une conversation)
            iterations: nombre d'échanges précédents sur le même sujet
                (utilisé par le Planner pour l'escalade du niveau d'aide)

        Returns:
            Réponse finale et métadonnées
        """
        logger.info(f"📥 Message reçu: {user_message[:100]}...")

        result = self._graph.invoke(
            user_message=user_message,
            student_id=student_id,
            session_id=session_id,
            context=context,
            iterations=iterations,
        )

        logger.info(f"📤 Réponse générée: {result.get('final_response', '')[:100]}...")

        return {
            "response": result.get("final_response", ""),
            "intent": result.get("intent", "general"),
            "level": result.get("level", "reformulation"),
            "confidence": result.get("confidence_score", 0.0),
            "responses": result.get("agent_responses", {}),
            "retrieved_docs": result.get("retrieved_docs", []),
            "math_tool_result": result.get("math_tool_result"),
            "progression_summary": result.get("progression_summary", {}),
            "timestamp": datetime.now().isoformat(),
        }
