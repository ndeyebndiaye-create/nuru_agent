# backend/app/api/dependencies/containers.py
"""
Injection de dépendances pour l'API.
"""
import logging
from datetime import datetime
import uuid

from backend.app.agents import OrchestratorAgent, AgentConfig
from backend.app.rag.vector_indexer import HybridRetriever, VectorIndexerConfig

logger = logging.getLogger(__name__)

# Instances globales (singletons)
_orchestrator = None
_retriever = None
_session_manager = None


def get_retriever():
    """Récupère l'instance du retriever."""
    global _retriever
    if _retriever is None:
        try:
            config = VectorIndexerConfig.from_env()
            _retriever = HybridRetriever(config)
            logger.info("✅ Retriever initialisé")
        except Exception as e:
            logger.error(f"❌ Erreur d'initialisation du retriever: {e}")
            _retriever = None
    return _retriever


def get_orchestrator():
    """Récupère l'instance de l'orchestrateur (graphe LangGraph)."""
    global _orchestrator
    if _orchestrator is None:
        try:
            config = AgentConfig()
            _orchestrator = OrchestratorAgent(
                config,
                retriever=get_retriever(),
            )
            logger.info("✅ Orchestrateur (LangGraph) initialisé")
        except Exception as e:
            logger.error(f"❌ Erreur d'initialisation de l'orchestrateur: {e}")
            raise
    return _orchestrator


class SimpleSessionManager:
    """Gestionnaire de sessions en mémoire (à remplacer par Redis en production)."""

    def __init__(self):
        self.sessions = {}

    def get(self, session_id):
        return self.sessions.get(session_id)

    def create(self, user_id=None):
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "user_id": user_id,
            "created_at": datetime.now(),
        }
        return session_id


def get_session_manager():
    """Récupère le gestionnaire de sessions (singleton)."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SimpleSessionManager()
    return _session_manager
