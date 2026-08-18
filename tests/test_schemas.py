"""
Testes dos schemas Pydantic (validação e normalização).
"""

import pytest
from pydantic import ValidationError

from app.schemas import TicketCreate, TicketUpdate


class TestTicketCreateSchema:
    """Testes do schema TicketCreate."""

    def test_valid_ticket_create(self):
        """Um TicketCreate válido deve ser aceito."""
        ticket = TicketCreate(description="Descrição válida.")
        assert ticket.description == "Descrição válida."
        assert ticket.title is None
        assert ticket.category is None
        assert ticket.priority is None

    def test_required_description(self):
        """description é obrigatório."""
        with pytest.raises(ValidationError):
            TicketCreate()

    def test_description_min_length(self):
        """description deve ter pelo menos 3 caracteres."""
        with pytest.raises(ValidationError):
            TicketCreate(description="ab")

    def test_description_max_length(self):
        """description deve ter no máximo 5000 caracteres."""
        with pytest.raises(ValidationError):
            TicketCreate(description="a" * 5001)

    def test_title_max_length(self):
        """title deve ter no máximo 200 caracteres."""
        with pytest.raises(ValidationError):
            TicketCreate(description="Descrição válida.", title="a" * 201)

    def test_priority_normalized_lowercase(self):
        """Prioridade 'media' deve ser normalizada para 'Média'."""
        ticket = TicketCreate(description="Descrição válida.", priority="media")
        assert ticket.priority == "Média"

    def test_priority_normalized_critica(self):
        """Prioridade 'critica' deve ser normalizada para 'Crítica'."""
        ticket = TicketCreate(description="Descrição válida.", priority="critica")
        assert ticket.priority == "Crítica"

    def test_priority_invalid(self):
        """Prioridade inválida deve levantar ValidationError."""
        with pytest.raises(ValidationError):
            TicketCreate(description="Descrição válida.", priority="Extrema")

    def test_category_normalized_lowercase(self):
        """Categoria 'financeiro' deve ser normalizada para 'Financeiro'."""
        ticket = TicketCreate(description="Descrição válida.", category="financeiro")
        assert ticket.category == "Financeiro"

    def test_category_invalid(self):
        """Categoria inválida deve levantar ValidationError."""
        with pytest.raises(ValidationError):
            TicketCreate(description="Descrição válida.", category="Inexistente")


class TestTicketUpdateSchema:
    """Testes do schema TicketUpdate."""

    def test_valid_ticket_update_empty(self):
        """Um TicketUpdate vazio é válido (PATCH de nada)."""
        ticket = TicketUpdate()
        assert ticket.title is None
        assert ticket.description is None
        assert ticket.category is None
        assert ticket.priority is None
        assert ticket.status is None

    def test_valid_ticket_update_fields(self):
        """Um TicketUpdate com campos válidos."""
        ticket = TicketUpdate(
            title="Novo título",
            description="Nova descrição.",
            category="Suporte",
            priority="Alta",
            status="em andamento",
        )
        assert ticket.title == "Novo título"
        assert ticket.description == "Nova descrição."
        assert ticket.category == "Suporte"
        assert ticket.priority == "Alta"
        assert ticket.status == "em andamento"

    def test_status_normalized(self):
        """Status 'EM ANDAMENTO' deve ser normalizado para minúsculo."""
        ticket = TicketUpdate(status="EM ANDAMENTO")
        assert ticket.status == "em andamento"

    def test_status_invalid(self):
        """Status inválido deve levantar ValidationError."""
        with pytest.raises(ValidationError):
            TicketUpdate(status="invalido")

    def test_priority_invalid(self):
        """Prioridade inválida deve levantar ValidationError."""
        with pytest.raises(ValidationError):
            TicketUpdate(priority="Extrema")