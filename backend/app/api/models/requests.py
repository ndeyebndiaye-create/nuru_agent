# backend/api/models/requests.py
"""
Modèles de requête pour l'API.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class ChatRequest(BaseModel):
    """Requête de chat."""
    message: str = Field(..., description="Message de l'utilisateur")
    session_id: Optional[str] = Field(None, description="ID de session")
    user_id: Optional[str] = Field(None, description="ID de l'utilisateur")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Contexte supplémentaire")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Explique-moi les dérivées",
                "session_id": "session_123",
                "user_id": "user_456",
                "context": {"chapitre": "Dérivabilité"}
            }
        }

class ChatResponse(BaseModel):
    """Réponse de chat."""
    response: str = Field(..., description="Réponse du système")
    intent: str = Field(..., description="Intention détectée")
    level: str = Field(..., description="Niveau d'aide")
    confidence: float = Field(..., description="Score de confiance")
    session_id: str = Field(..., description="ID de session")
    timestamp: datetime = Field(default_factory=datetime.now, description="Horodatage")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "La dérivée est un concept fondamental...",
                "intent": "cours",
                "level": "rappel",
                "confidence": 0.85,
                "session_id": "session_123",
                "timestamp": "2024-01-15T10:30:00"
            }
        }

class FeedbackRequest(BaseModel):
    """Requête de feedback."""
    session_id: str = Field(..., description="ID de session")
    rating: int = Field(ge=1, le=5, description="Note de 1 à 5")
    comment: Optional[str] = Field(None, description="Commentaire")
    helpful: bool = Field(..., description="La réponse a-t-elle été utile ?")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_123",
                "rating": 4,
                "comment": "Très bonne explication",
                "helpful": True
            }
        }

class SearchRequest(BaseModel):
    """Requête de recherche."""
    query: str = Field(..., description="Requête de recherche")
    top_k: Optional[int] = Field(10, description="Nombre de résultats")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Filtres")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "dérivée fonction exponentielle",
                "top_k": 5,
                "filters": {"chapitre": "Dérivabilité"}
            }
        }

class SearchResponse(BaseModel):
    """Réponse de recherche."""
    results: List[Dict[str, Any]] = Field(..., description="Résultats de recherche")
    total: int = Field(..., description="Nombre total de résultats")
    query: str = Field(..., description="Requête originale")
    
    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "id": "doc_1",
                        "text": "La dérivée de e^x est e^x",
                        "score": 0.95,
                        "metadata": {"chapitre": "Fonctions Exponentielles"}
                    }
                ],
                "total": 1,
                "query": "dérivée fonction exponentielle"
            }
        }