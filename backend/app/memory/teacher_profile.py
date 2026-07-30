# backend/app/memory/teacher_profile.py
"""
Gestion des comptes enseignants : inscription, authentification, et suivi
des élèves liés à leur compte.

Authentification volontairement simple (hash PBKDF2 stdlib + jeton de
session opaque en base) : pas de dépendance externe (bcrypt/passlib),
suffisant pour un déploiement mono-instance / démo. À durcir (rotation de
jetons, expiration, etc.) avant une mise en production à plus grande échelle.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import datetime
from typing import Any, Dict, List, Optional

from .db import get_session
from .models import Teacher, TeacherStudent, Student

_PBKDF2_ITERATIONS = 260_000


def _hash_password(password: str, salt: Optional[bytes] = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split("$", 1)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
    except (ValueError, AttributeError):
        return False
    computed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return hmac.compare_digest(computed, expected)


class TeacherAuthError(Exception):
    """Erreur d'inscription ou d'authentification enseignant."""


def register_teacher(email: str, password: str, name: Optional[str] = None) -> str:
    """Crée un compte enseignant. Retourne l'id enseignant."""
    with get_session() as session:
        existing = session.query(Teacher).filter_by(email=email.lower().strip()).first()
        if existing:
            raise TeacherAuthError("Un compte existe déjà avec cet email.")

        teacher = Teacher(
            email=email.lower().strip(),
            password_hash=_hash_password(password),
            name=name,
        )
        session.add(teacher)
        session.flush()
        return teacher.id


def authenticate_teacher(email: str, password: str) -> Dict[str, Any]:
    """Vérifie les identifiants. Retourne {id, email, name} si valide."""
    with get_session() as session:
        teacher = session.query(Teacher).filter_by(email=email.lower().strip()).first()
        if not teacher or not _verify_password(password, teacher.password_hash):
            raise TeacherAuthError("Email ou mot de passe incorrect.")
        return {"id": teacher.id, "email": teacher.email, "name": teacher.name}


def link_student(teacher_id: str, student_external_id: str) -> None:
    """Lie un élève (par son identifiant externe) au compte enseignant."""
    from .student_profile import get_or_create_student

    student_id = get_or_create_student(external_user_id=student_external_id)

    with get_session() as session:
        existing = (
            session.query(TeacherStudent)
            .filter_by(teacher_id=teacher_id, student_id=student_id)
            .first()
        )
        if not existing:
            session.add(TeacherStudent(teacher_id=teacher_id, student_id=student_id))


def get_linked_students(teacher_id: str) -> List[Dict[str, Any]]:
    """Liste les élèves suivis par un enseignant."""
    with get_session() as session:
        links = session.query(TeacherStudent).filter_by(teacher_id=teacher_id).all()
        result = []
        for link in links:
            student = session.query(Student).filter_by(id=link.student_id).first()
            if student:
                result.append({
                    "student_id": student.id,
                    "external_user_id": student.external_user_id,
                    "name": student.name,
                    "classe": student.classe,
                    "serie": student.serie,
                    "linked_at": link.linked_at.isoformat() if link.linked_at else None,
                })
        return result
