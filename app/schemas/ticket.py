"""
Schemas Pydantic de Ticket (validação e serialização).
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.constants import (
    PRIORITY_ALIASES,
    VALID_CATEGORIES,
    VALID_PRIORITIES,
    VALID_STATUSES,
)


# Conjuntos em minúsculo para comparação
_VALID_CATEGORIES_LOWER = {c.lower() for c in VALID_CATEGORIES}
_VALID_PRIORITIES_LOWER = {p.lower() for p in VALID_PRIORITIES}
_VALID_STATUSES_LOWER = {s.lower() for s in VALID_STATUSES}


def _normalize_priority(value: str) -> str:
    """Normaliza a prioridade para o formato canônico (ex: 'media' -> 'Média')."""
    value_lower = value.strip().lower()

    # Verifica aliases (ex: "media" -> "Média", "critica" -> "Crítica")
    if value_lower in PRIORITY_ALIASES:
        return PRIORITY_ALIASES[value_lower]

    if value_lower not in _VALID_PRIORITIES_LOWER:
        raise ValueError(f"Prioridade inválida: {value}. Use: Baixa, Média, Alta ou Crítica.")
    for valid in VALID_PRIORITIES:
        if valid.lower() == value_lower:
            return valid
    raise ValueError(f"Prioridade inválida: {value}.")


def _normalize_category(value: str) -> str:
    """Normaliza a categoria para o formato canônico (ex.: 'financeiro' -> 'Financeiro')."""
    value_lower = value.strip().lower()
    if value_lower not in _VALID_CATEGORIES_LOWER:
        raise ValueError(
            f"Categoria inválida: {value}. Use: Bug, Suporte, Melhoria, Financeiro, Infraestrutura ou Outro."
        )
    for valid in VALID_CATEGORIES:
        if valid.lower() == value_lower:
            return valid
    raise ValueError(f"Categoria inválida: {value}.")


class TicketBase(BaseModel):
    """Campos comuns entre criação e leitura."""

    title: str | None = Field(
        None,
        max_length=200,
        description="Título do chamado (opcional). Se não informado, será extraído da descrição.",
    )
    description: str = Field(
        ...,
        min_length=3,
        max_length=5000,
        description="Descrição textual do chamado.",
    )
    category: str | None = Field(None, max_length=50, description="Categoria do chamado")
    priority: str | None = Field(None, max_length=20, description="Prioridade (baixa, média, alta, crítica)")

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str | None) -> str | None:
        """Valida e normaliza a prioridade se informada."""
        if v is None:
            return v
        return _normalize_priority(v)

    @field_validator("category", mode="before")
    @classmethod
    def validate_category(cls, v: str | None) -> str | None:
        """Valida e normaliza a categoria se informada."""
        if v is None:
            return v
        return _normalize_category(v)


class TicketClassification(BaseModel):
    """
    Contrato de saída estruturada do LLM para classificação de chamados.

    O modelo deve produzir uma resposta JSON com estes campos, que são
    validados e normalizados para os valores canônicos do domínio.
    """

    title: str
    category: str
    priority: str

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Valida e normaliza a prioridade retornada pelo LLM."""
        return _normalize_priority(v)

    @field_validator("category", mode="before")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Valida e normaliza a categoria retornada pelo LLM."""
        return _normalize_category(v)


class TicketCreate(TicketBase):
    """Dados necessários para criar um novo ticket."""


class TicketUpdate(BaseModel):
    """Dados opcionais para atualizar um ticket existente."""

    title: str | None = Field(None, min_length=3, max_length=200)
    description: str | None = Field(None, min_length=3, max_length=5000)
    category: str | None = None
    priority: str | None = None
    status: str | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        """Valida o status se informado."""
        if v is None:
            return v
        status = v.strip().lower()
        if status not in _VALID_STATUSES_LOWER:
            raise ValueError(
                f"Status inválido: {v}. Use: aberto, em andamento, resolvido ou fechado."
            )
        return status

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str | None) -> str | None:
        """Valida a prioridade se informada."""
        if v is None:
            return v
        return _normalize_priority(v)

    @field_validator("category", mode="before")
    @classmethod
    def validate_category(cls, v: str | None) -> str | None:
        """Valida a categoria se informada."""
        if v is None:
            return v
        return _normalize_category(v)


class TicketRead(TicketBase):
    """Representação completa de um ticket retornado pela API."""

    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketResponse(TicketRead):
    """Alias de saída para compatibilidade (mesmos campos do TicketRead)."""


class TicketListResponse(BaseModel):
    """Resposta paginada da listagem de chamados."""

    total: int
    items: list[TicketResponse]