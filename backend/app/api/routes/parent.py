# backend/app/api/routes/parent.py
"""
Routes de l'espace Parent : consultation en temps réel de l'activité,
des résultats, badges et temps d'étude réels des enfants associés.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/parent", tags=["Parent"])


def _ensure_memory():
    from backend.app.memory import student_profile, auth_service
    student_profile.ensure_initialized()
    auth_service.ensure_super_admin()


@router.get("/students/{parent_id}")
async def get_parent_students(parent_id: str):
    _ensure_memory()
    from backend.app.memory.auth_service import get_parent_students_data

    try:
        students_data = get_parent_students_data(parent_id)
        return {"parent_id": parent_id, "students": students_data}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


class LinkChildRequest(BaseModel):
    parent_id: str
    student_identifier: str


@router.post("/link-child")
async def link_child(payload: LinkChildRequest):
    _ensure_memory()
    from backend.app.memory.auth_service import link_student_public, AuthError

    try:
        return link_student_public(payload.parent_id, "parent", payload.student_identifier)
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
