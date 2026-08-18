"""
AI Ticket Agent API

Fase 1 — Criar a API de chamados:
Recebe um chamado textual e o devolve estruturado.

Exemplo:
    POST /tickets/
    {"description": "A API de pagamentos está retornando erro 500."}
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.db.session import Base, engine
from app.routers import tickets

# Garante que os modelos sejam registrados no metadata do SQLAlchemy
import app.models  # noqa: F401


# Cria as tabelas no banco em memória
@asynccontextmanager
async def lifespan(_: FastAPI):
    # Cria as tabelas ao iniciar a aplicação
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(tickets.router, prefix=settings.API_PREFIX)


@app.get("/", tags=["health"])
def health_check():
    """Health check da API."""
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )