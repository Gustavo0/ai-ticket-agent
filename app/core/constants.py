"""
Constantes de domínio da aplicação.

Centraliza os valores válidos de categorias, prioridades e status para
evitar duplicação entre schemas, serviços e modelos.
"""

from enum import Enum


class TicketStatus(str, Enum):
    """Status possíveis de um chamado."""

    ABERTO = "aberto"
    EM_ANDAMENTO = "em andamento"
    RESOLVIDO = "resolvido"
    FECHADO = "fechado"


class TicketPriority(str, Enum):
    """Prioridades possíveis de um chamado."""

    BAIXA = "Baixa"
    MEDIA = "Média"
    ALTA = "Alta"
    CRITICA = "Crítica"


class TicketCategory(str, Enum):
    """Categorias possíveis de um chamado."""

    BUG = "Bug"
    SUPORTE = "Suporte"
    MELHORIA = "Melhoria"
    FINANCEIRO = "Financeiro"
    INFRAESTRUTURA = "Infraestrutura"
    OUTRO = "Outro"


# --- Conjuntos de valores válidos (para validação) ---
VALID_STATUSES = {status.value for status in TicketStatus}
VALID_PRIORITIES = {priority.value for priority in TicketPriority}
VALID_CATEGORIES = {category.value for category in TicketCategory}

# Mapeamento de aliases para normalização
PRIORITY_ALIASES: dict[str, str] = {
    "media": TicketPriority.MEDIA.value,
    "critica": TicketPriority.CRITICA.value,
}

CATEGORY_ALIASES: dict[str, str] = {
    "bug": TicketCategory.BUG.value,
    "suporte": TicketCategory.SUPORTE.value,
    "melhoria": TicketCategory.MELHORIA.value,
    "financeiro": TicketCategory.FINANCEIRO.value,
    "infraestrutura": TicketCategory.INFRAESTRUTURA.value,
    "outro": TicketCategory.OUTRO.value,
}

# --- Limites de validação ---
TITLE_MIN_LENGTH = 3
TITLE_MAX_LENGTH = 200
DESCRIPTION_MIN_LENGTH = 3
DESCRIPTION_MAX_LENGTH = 5000

# --- Paginação ---
DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 500