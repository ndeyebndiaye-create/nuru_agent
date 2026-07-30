# tests/test_auth_and_roles.py
"""
Tests unitaires et d'intégration pour :
- Inscription et authentification des rôles (Élève, Enseignant, Parent)
- Interdiction stricte de créer un compte Admin via l'inscription publique
- Super-Admin unique
- Liaison Parent <-> Élève & Enseignant <-> Élève
- Statistiques Admin en temps réel (COUNT())
- État initial élève (0% empty state)
"""
import pytest
from backend.app.memory.db import init_db, get_session, engine
from backend.app.memory.models import Base, User, Student, ParentStudent, TeacherStudent, ExerciseResult, ConceptMastery
from backend.app.memory.auth_service import (
    register_user,
    authenticate_user,
    ensure_super_admin,
    link_student_public,
    get_parent_students_data,
    get_teacher_students_data,
    get_admin_statistics,
    AuthError
)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    init_db()
    ensure_super_admin()
    yield


def test_super_admin_exists():
    stats = get_admin_statistics()
    assert stats["roles_breakdown"]["admin"] == 1


def test_admin_registration_forbidden():
    with pytest.raises(AuthError, match="strictement interdite"):
        register_user(
            email="hackadmin@nuru.sn",
            password="password123",
            role="admin",
            name="Hacker Admin"
        )


def test_register_public_roles():
    st = register_user(
        email="moussa.test@nuru.sn",
        password="password123",
        role="student",
        name="Moussa Test",
        classe="Terminale",
        serie="S1"
    )
    assert st["role"] == "student"
    assert st["student_id"] is not None

    tch = register_user(
        email="prof.test@nuru.sn",
        password="password123",
        role="teacher",
        name="Professeur Test"
    )
    assert tch["role"] == "teacher"

    prt = register_user(
        email="parent.test@nuru.sn",
        password="password123",
        role="parent",
        name="Parent Test",
        linked_student_identifier="moussa.test@nuru.sn"
    )
    assert prt["role"] == "parent"


def test_authenticate_user():
    user = authenticate_user("admin@nuru.sn", "admin123")
    assert user["role"] == "admin"
    assert user["email"] == "admin@nuru.sn"


def test_parent_and_teacher_student_linking():
    st = register_user(
        email="eleve.link@nuru.sn",
        password="password123",
        role="student",
        name="Élève Linked"
    )
    prt = register_user(
        email="parent.link@nuru.sn",
        password="password123",
        role="parent",
        name="Parent Linked"
    )
    tch = register_user(
        email="prof.link@nuru.sn",
        password="password123",
        role="teacher",
        name="Prof Linked"
    )

    # Link parent -> student
    res_p = link_student_public(prt["id"], "parent", st["email"])
    assert res_p["status"] == "success"

    # Link teacher -> student
    res_t = link_student_public(tch["id"], "teacher", st["email"])
    assert res_t["status"] == "success"

    p_data = get_parent_students_data(prt["id"])
    assert len(p_data) == 1
    assert p_data[0]["name"] == "Élève Linked"
    # Initial state must be empty / 0%
    assert p_data[0]["nb_evaluations"] == 0
    assert p_data[0]["overall_mastery"] == 0.0

    t_data = get_teacher_students_data(tch["id"])
    assert len(t_data) == 1
    assert t_data[0]["name"] == "Élève Linked"


def test_real_admin_statistics():
    stats = get_admin_statistics()
    assert "total_users" in stats
    assert "roles_breakdown" in stats
    assert stats["roles_breakdown"]["admin"] == 1
