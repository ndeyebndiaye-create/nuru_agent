# backend/app/api/routes/auth.py
"""
Routes d'authentification et d'inscription réelles :
- /auth/register : Inscription sous rôles Élève, Enseignant, Parent (Admin strictement interdit)
- /auth/login    : Connexion réelle avec vérification de mot de passe
- /auth/link-student : Liaison d'un élève à un compte Parent ou Enseignant
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

logger = logging.getLogger(__name__) if 'logging' in globals() else __import__('logging').getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentification"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str
    role: str = Field(..., description="student | teacher | parent")
    classe: Optional[str] = "Terminale"
    serie: Optional[str] = "S1"
    linked_student_identifier: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LinkStudentRequest(BaseModel):
    user_id: str
    role: str
    student_identifier: str


def _ensure_memory():
    from backend.app.memory import student_profile, auth_service
    student_profile.ensure_initialized()
    auth_service.ensure_super_admin()


@router.post("/register")
async def register(payload: RegisterRequest):
    _ensure_memory()
    from backend.app.memory.auth_service import register_user, AuthError

    try:
        user_data = register_user(
            email=payload.email,
            password=payload.password,
            role=payload.role,
            name=payload.name,
            classe=payload.classe or "Terminale",
            serie=payload.serie or "S1",
            linked_student_identifier=payload.linked_student_identifier,
        )
        return user_data
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error(f"Erreur inscription: {exc}")
        raise HTTPException(status_code=500, detail="Erreur interne lors de l'inscription.")


@router.post("/login")
async def login(payload: LoginRequest):
    _ensure_memory()
    from backend.app.memory.auth_service import authenticate_user, AuthError

    try:
        user_data = authenticate_user(email=payload.email, password=payload.password)
        return user_data
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    except Exception as exc:
        logger.error(f"Erreur connexion: {exc}")
        raise HTTPException(status_code=500, detail="Erreur interne lors de la connexion.")


@router.post("/link-student")
async def link_student(payload: LinkStudentRequest):
    _ensure_memory()
    from backend.app.memory.auth_service import link_student_public, AuthError

    try:
        return link_student_public(payload.user_id, payload.role, payload.student_identifier)
    except AuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
