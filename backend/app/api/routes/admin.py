# backend/app/api/routes/admin.py
"""
Routes d'administration : métriques en temps réel issues des requêtes
en base de données (COUNT() réels, ventilation des rôles, volume RAG/cours).
"""
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/admin", tags=["Administration"])


def _ensure_memory():
    from backend.app.memory import student_profile, auth_service
    student_profile.ensure_initialized()
    auth_service.ensure_super_admin()


@router.get("/stats")
async def get_admin_stats():
    """Retourne les métriques de base de données réelles (compte de chaque rôle, évaluations, etc.)."""
    _ensure_memory()
    from backend.app.memory.auth_service import get_admin_statistics

    try:
        return get_admin_statistics()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/users")
async def list_admin_users():
    """Liste tous les comptes enregistrés en base de données."""
    _ensure_memory()
    from backend.app.memory.auth_service import get_all_users_admin

    try:
        users = get_all_users_admin()
        return {"users": users, "total": len(users)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
