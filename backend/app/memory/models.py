# backend/app/memory/models.py
"""
Modèles SQLAlchemy pour la mémoire élève.

Tables :
- students          : profil de l'élève (classe, série, préférences)
- interactions       : historique des échanges (question, intention, niveau)
- exercise_results   : résultats d'exercices / quiz (pour l'agent Evaluation)
- concept_mastery    : niveau de maîtrise par notion (pour l'agent Progression)
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def _uuid() -> str:
    return str(uuid.uuid4())


class Student(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True, default=_uuid)
    external_user_id = Column(String, unique=True, nullable=True, index=True)
    name = Column(String, nullable=True)
    classe = Column(String, default="Terminale")
    serie = Column(String, default="S1")
    created_at = Column(DateTime, default=datetime.utcnow)

    interactions = relationship("Interaction", back_populates="student", cascade="all, delete-orphan")
    results = relationship("ExerciseResult", back_populates="student", cascade="all, delete-orphan")
    mastery = relationship("ConceptMastery", back_populates="student", cascade="all, delete-orphan")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(String, primary_key=True, default=_uuid)
    student_id = Column(String, ForeignKey("students.id"), nullable=False, index=True)
    session_id = Column(String, index=True, nullable=True)
    user_message = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    level = Column(String, nullable=True)
    concept = Column(String, nullable=True)
    response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="interactions")


class ExerciseResult(Base):
    __tablename__ = "exercise_results"

    id = Column(String, primary_key=True, default=_uuid)
    student_id = Column(String, ForeignKey("students.id"), nullable=False, index=True)
    concept = Column(String, nullable=True)
    chapitre = Column(String, nullable=True)
    exercise_type = Column(String, default="exercice")  # exercice | quiz
    difficulty = Column(String, default="intermediate")
    is_correct = Column(Boolean, nullable=True)
    score = Column(Float, nullable=True)  # ex: 0.0 à 1.0 pour quiz à plusieurs questions
    details = Column(JSON, nullable=True)  # réponses, erreurs détectées, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="results")


class ConceptMastery(Base):
    __tablename__ = "concept_mastery"

    id = Column(String, primary_key=True, default=_uuid)
    student_id = Column(String, ForeignKey("students.id"), nullable=False, index=True)
    concept = Column(String, nullable=False)
    chapitre = Column(String, nullable=True)
    mastery_score = Column(Float, default=0.0)  # 0.0 (non maîtrisé) à 1.0 (maîtrisé)
    attempts = Column(Integer, default=0)
    successes = Column(Integer, default=0)
    last_seen = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="mastery")


class User(Base):
    """Compte utilisateur unifié (Élève, Enseignant, Parent, Admin)."""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False, index=True)  # student | teacher | parent | admin
    classe = Column(String, default="Terminale")
    serie = Column(String, default="S1")
    created_at = Column(DateTime, default=datetime.utcnow)


class ParentStudent(Base):
    """Table de liaison Parent <-> Élèves suivis."""
    __tablename__ = "parent_students"

    id = Column(String, primary_key=True, default=_uuid)
    parent_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False, index=True)
    linked_at = Column(DateTime, default=datetime.utcnow)


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(String, primary_key=True, default=_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    students = relationship("TeacherStudent", back_populates="teacher", cascade="all, delete-orphan")


class TeacherStudent(Base):
    """Table de liaison enseignant <-> élèves suivis."""
    __tablename__ = "teacher_students"

    id = Column(String, primary_key=True, default=_uuid)
    teacher_id = Column(String, ForeignKey("teachers.id"), nullable=False, index=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False, index=True)
    linked_at = Column(DateTime, default=datetime.utcnow)

    teacher = relationship("Teacher", back_populates="students")


class Recommendation(Base):
    """Recommandation d'exercice / révision envoyée par un enseignant à un élève."""
    __tablename__ = "recommendations"

    id = Column(String, primary_key=True, default=_uuid)
    teacher_id = Column(String, nullable=False, index=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False, index=True)
    concept = Column(String, nullable=False)
    chapitre = Column(String, nullable=True)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Badge(Base):
    """Badge de motivation/gamification débloqué par un élève."""
    __tablename__ = "badges"

    id = Column(String, primary_key=True, default=_uuid)
    student_id = Column(String, ForeignKey("students.id"), nullable=False, index=True)
    code = Column(String, nullable=False)  # ex: "premier_quiz", "10_exercices", "maitrise_derivation"
    label = Column(String, nullable=False)
    description = Column(String, nullable=True)
    earned_at = Column(DateTime, default=datetime.utcnow)
