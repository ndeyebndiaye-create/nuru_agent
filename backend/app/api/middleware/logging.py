# backend/api/middleware/logging.py
"""
Middleware pour le logging des requêtes.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour logger les requêtes et réponses.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Log de la requête
        start_time = time.time()
        
        # Corps de la requête (pour POST/PUT)
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                body = body.decode("utf-8")[:500]  # Limiter pour éviter les logs trop longs
            except:
                body = "Unable to read body"
        
        logger.info(f"📥 {request.method} {request.url.path}")
        if body:
            logger.debug(f"   Body: {body}")
        
        # Traiter la requête
        try:
            response = await call_next(request)
            
            # Log de la réponse
            elapsed_time = time.time() - start_time
            logger.info(f"📤 {request.method} {request.url.path} -> {response.status_code} ({elapsed_time:.3f}s)")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur dans {request.url.path}: {e}")
            raise