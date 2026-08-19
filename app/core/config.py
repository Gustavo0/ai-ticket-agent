"""
Configurações centralizadas da aplicação.

Usa Pydantic Settings para carregar variáveis de ambiente com defaults seguros.
Permite sobrescrever configurações via variáveis de ambiente ou arquivo .env.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações da aplicação.

    Todas as configurações podem ser sobrescritas por variáveis de ambiente
    ou por um arquivo `.env` na raiz do projeto.
    """

    # --- Aplicação ---
    APP_NAME: str = "AI Ticket Agent API"
    APP_VERSION: str = "0.2.0"
    APP_DESCRIPTION: str = (
        "API de chamados de suporte técnico.\n\n"
        "**Fase 1**: Recebe um chamado em texto livre e o devolve estruturado "
        "com título, categoria, prioridade e status."
    )
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # --- Servidor ---
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # --- Banco de dados ---
    # SQLite em memória por padrão (equivalente ao H2 em memória do Java).
    # Para usar outro banco, defina DATABASE_URL no .env.
    DATABASE_URL: str = "sqlite://"
    DB_ECHO: bool = False

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["*"]

    # --- LLM (Ollama / OpenAI) ---
    # Provedor de LLM a ser usado: "ollama" (padrão, gratuito) ou "openai".
    LLM_PROVIDER: str = "ollama"

    # Configuração do Ollama (padrão)
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA_MODEL: str = "llama3.2"

    # Configuração do OpenAI (legado - não usado pelo novo LLMClassifier)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-5-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Retorna a instância única (cacheada) das configurações.

    Uso:
        from app.core.config import get_settings
        settings = get_settings()
    """
    return Settings()


settings = get_settings()