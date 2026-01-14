# futurisys-ml-deploy/src/db/session.py

import os
from typing import AsyncGenerator

from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# ============================================================
# Configuration lazy (sécurisée & testable)
# ============================================================


def get_database_url() -> str:
    """
    Récupère la DATABASE_URL depuis l'environnement.
    Le check est volontairement fait à l'exécution
    (et non à l'import) pour permettre les tests.
    """
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    return database_url


def get_engine():
    """
    Crée le moteur SQLAlchemy async à la demande.
    Compatible PostgreSQL (Neon, RDS, Supabase).
    """
    url = make_url(get_database_url()).set(query={})

    return create_async_engine(
        url,
        echo=False,
        connect_args={"ssl": "require"},
    )


# ============================================================
# Session factory (lazy)
# ============================================================

_async_session_factory = None


def get_async_session_factory():
    global _async_session_factory

    if _async_session_factory is None:
        engine = get_engine()
        _async_session_factory = async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
        )

    return _async_session_factory


# ============================================================
# Dépendance FastAPI
# ============================================================


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dépendance FastAPI injectant une AsyncSession.
    Overridable proprement en tests.
    """
    async_session_factory = get_async_session_factory()

    async with async_session_factory() as session:
        yield session
