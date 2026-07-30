# backend/app/memory/db.py
"""
Connexion base de données pour la couche mémoire élève.

Utilise PostgreSQL en production (variable d'environnement DATABASE_URL,
ex: postgresql+psycopg://user:pass@host:5432/nuru) et retombe sur SQLite
en local si aucune URL n'est fournie, pour permettre de développer et
tester sans dépendance externe.
"""
from __future__ import annotations

import os
import logging
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)

DEFAULT_SQLITE_URL = "sqlite:///./nuru_student_memory.db"


def _get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        # Normalise le préfixe legacy 'postgres://' (Heroku-style) -> SQLAlchemy
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        return url
    logger.info("ℹ️ DATABASE_URL non défini, utilisation de SQLite local (%s)", DEFAULT_SQLITE_URL)
    return DEFAULT_SQLITE_URL


DATABASE_URL = _get_database_url()

_engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Crée les tables si elles n'existent pas encore."""
    from . import models  # noqa: F401  (assure l'enregistrement des modèles)
    from .models import Base

    Base.metadata.create_all(bind=engine)
    logger.info("✅ Base de données mémoire élève initialisée (%s)", DATABASE_URL.split("://")[0])


@contextmanager
def get_session():
    """Context manager fournissant une session SQLAlchemy avec commit/rollback auto."""
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
