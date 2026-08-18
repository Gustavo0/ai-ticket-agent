"""
Fixtures compartilhadas para os testes pytest.
"""

import pytest
from fastapi.testclient import TestClient

from app.db.session import Base, engine
from app.db.session import SessionLocal
from main import app


@pytest.fixture()
def client():
    """
    Fixture que cria um TestClient para a aplicação FastAPI.

    As tabelas são recriadas antes de cada teste, garantindo
    um banco de dados limpo e isolado.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db_session():
    """
    Fixture que fornece uma sessão de banco de dados isolada.

    Cada teste recebe uma nova sessão, garantindo isolamento
    entre os testes.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()