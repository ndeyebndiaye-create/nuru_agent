# backend/agents/state.py
"""
Gestion de l'état des agents.
"""
from typing import Dict, Any, List, Optional, TypedDict
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class AgentState:
    """État partagé entre les agents."""
    
    # Message de l'utilisateur
    user_message: str = ""
    
    # Contexte
    context: Dict[str, Any] = field(default_factory=dict)
    retrieved_docs: List[Dict[str, Any]] = field(default_factory=list)
    
    # Planification
    intent: str = "unknown"  # cours, exercice, quiz, calcul, general
    required_agents: List[str] = field(default_factory=list)
    required_tools: List[str] = field(default_factory=list)
    current_level: str = "reformulation"
    
    # Historique
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    iterations: int = 0
    max_iterations: int = 5
    
    # Réponses
    agent_responses: Dict[str, str] = field(default_factory=dict)
    final_response: str = ""
    
    # Évaluation
    confidence_score: float = 0.0
    needs_verification: bool = True
    verified: bool = False
    
    # Métadonnées
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return {
            "user_message": self.user_message,
            "context": self.context,
            "intent": self.intent,
            "current_level": self.current_level,
            "conversation_history": self.conversation_history,
            "final_response": self.final_response,
            "confidence_score": self.confidence_score,
            "timestamp": self.timestamp
        }
    
    def add_to_history(self, role: str, content: str):
        """Ajoute un message à l'historique."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def increment_iterations(self):
        """Incrémente le compteur d'itérations."""
        self.iterations += 1
        return self.iterations <= self.max_iterations

class GraphState(TypedDict, total=False):
    """État utilisé par le graphe LangGraph (backend.app.agents.graph).

    LangGraph attend un schéma "plat" (TypedDict) pour fusionner les mises
    à jour retournées par chaque nœud. On garde volontairement une
    structure simple ; AgentState (ci-dessus) reste utilisé en interne par
    certains agents historiques via un petit adaptateur.
    """

    # Entrée
    user_message: str
    context: Dict[str, Any]
    student_id: Optional[str]
    session_id: Optional[str]

    # Plan (sortie du Planner)
    intent: str
    level: str
    required_agents: List[str]
    required_tools: List[str]
    parameters: Dict[str, Any]

    # Contexte récupéré (sortie du Retriever)
    retrieved_docs: List[Dict[str, Any]]
    course_docs: List[Dict[str, Any]]
    supplement_docs: List[Dict[str, Any]]
    has_course: bool
    prompt_context: str

    # Résultats des agents spécialisés
    agent_responses: Dict[str, Any]
    math_tool_result: Optional[Dict[str, Any]]

    # Vérification
    verification: Dict[str, Any]

    # Progression / évaluation
    progression_summary: Dict[str, Any]

    # Sortie finale
    final_response: str
    confidence_score: float

    # Compteur d'itérations (pour l'escalade de niveau d'aide)
    iterations: int
