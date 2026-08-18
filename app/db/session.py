"""
Configuração da conexão com o banco de dados.

Usa SQLite em memória por padrão (equivalente ao H2 em memória do Java).
Para usar outro banco, defina a variável de ambiente `DATABASE_URL`.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings


def _create_engine_kwargs() -> dict:
    """Retorna os argumentos do engine de acordo com o banco configurado."""
    kwargs: dict = {"echo": settings.DB_ECHO}

    if settings.DATABASE_URL == "sqlite://" or settings.DATABASE_URL.startswith("sqlite"):
        # SQLite em memória exige configurações específicas
        kwargs["connect_args"] = {"check_same_thread": False}
        if settings.DATABASE_URL == "sqlite://":
            kwargs["poolclass"] = StaticPool

    return kwargs


engine = create_engine(settings.DATABASE_URL, **_create_engine_kwargs())

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Classe base para todos os modelos ORM."""


def get_db() -> Generator[Session, None, None]:
    """
    Dependency do FastAPI para obter uma sessão de banco.
    Garante que a sessão seja fechada após a requisição.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()