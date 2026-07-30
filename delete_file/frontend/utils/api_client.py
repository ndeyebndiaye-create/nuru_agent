# frontend/utils/api_client.py
"""
Client pour communiquer avec l'API FastAPI.
"""
import requests
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class APIClient:
    """
    Client pour l'API NURU.
    """
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session_id = None
    
    def set_session(self, session_id: str):
        """Définit l'ID de session."""
        self.session_id = session_id
    
    def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Envoie un message au chat.
        """
        try:
            payload = {
                "message": message,
                "session_id": self.session_id,
                "context": context or {}
            }
            
            response = requests.post(
                f"{self.base_url}/chat/",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                # Mettre à jour l'ID de session
                if "session_id" in data:
                    self.session_id = data["session_id"]
                return data
            else:
                return {
                    "response": f"❌ Erreur: {response.status_code}",
                    "intent": "error",
                    "level": "error",
                    "confidence": 0
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "response": "❌ Impossible de se connecter à l'API. Vérifie que l'API est en cours d'exécution.",
                "intent": "error",
                "level": "error",
                "confidence": 0
            }
        except Exception as e:
            return {
                "response": f"❌ Erreur: {str(e)}",
                "intent": "error",
                "level": "error",
                "confidence": 0
            }
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Recherche dans la base de connaissances.
        """
        try:
            response = requests.post(
                f"{self.base_url}/chat/search",
                json={"query": query, "top_k": top_k}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])
            return []
            
        except Exception as e:
            logger.error(f"Erreur de recherche: {e}")
            return []
    
    def health_check(self) -> bool:
        """
        Vérifie si l'API est accessible.
        """
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def send_feedback(self, rating: int, comment: str, helpful: bool) -> bool:
        """
        Envoie un feedback.
        """
        try:
            response = requests.post(
                f"{self.base_url}/chat/feedback",
                json={
                    "session_id": self.session_id,
                    "rating": rating,
                    "comment": comment,
                    "helpful": helpful
                }
            )
            return response.status_code == 204
        except:
            return False