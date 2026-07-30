# backend/api/models/responses.py
"""
Modèles de réponse pour l'API.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class HealthResponse(BaseModel):
    """Réponse de santé."""
    status: str = Field(..., description="Statut du service")
    version: str = Field(..., description="Version de l'API")
    timestamp: datetime = Field(default_factory=datetime.now, description="Horodatage")
    services: Dict[str, str] = Field(default_factory=dict, description="Statut des services")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2024-01-15T10:30:00",
                "services": {
                    "qdrant": "connected",
                    "agents": "ready"
                }
            }
        }

class ErrorResponse(BaseModel):
    """Réponse d'erreur."""
    error: str = Field(..., description="Message d'erreur")
    code: str = Field(..., description="Code d'erreur")
    details: Optional[Dict[str, Any]] = Field(None, description="Détails supplémentaires")
    timestamp: datetime = Field(default_factory=datetime.now, description="Horodatage")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Service Qdrant indisponible",
                "code": "SERVICE_UNAVAILABLE",
                "details": {"service": "qdrant", "url": "https://cloud.qdrant.io"},
                "timestamp": "2024-01-15T10:30:00"
            }
        }

class SessionResponse(BaseModel):
    """Réponse de session."""
    session_id: str = Field(..., description="ID de session")
    created_at: datetime = Field(..., description="Date de création")
    expires_at: datetime = Field(..., description="Date d'expiration")
    user_id: Optional[str] = Field(None, description="ID de l'utilisateur")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Métadonnées")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_123",
                "created_at": "2024-01-15T10:30:00",
                "expires_at": "2024-01-15T18:30:00",
                "user_id": "user_456",
                "metadata": {"classe": "Terminale", "serie": "S1"}
            }
        }
