"""
Testes do endpoint de criação de tickets (POST /api/v1/tickets/).
"""


class TestCreateTicket:
    """Testes de criação de chamados."""

    def test_create_ticket_returns_201(self, client):
        """Criar um chamado deve retornar status 201."""
        response = client.post(
            "/api/v1/tickets/",
            json={"description": "A API de pagamentos está retornando erro 500."},
        )
        assert response.status_code == 201

    def test_create_ticket_generates_id(self, client):
        """Um chamado criado deve receber um ID."""
        response = client.post(
            "/api/v1/tickets/",
            json={"description": "A API de pagamentos está retornando erro 500."},
        )
        assert response.json()["id"] == 1

    def test_create_ticket_preserves_description(self, client):
        """A descrição enviada deve ser preservada no chamado criado."""
        description = "A API de pagamentos está retornando erro 500."
        response = client.post("/api/v1/tickets/", json={"description": description})
        assert response.json()["description"] == description

    def test_create_ticket_infers_title(self, client):
        """O título deve ser inferido a partir da descrição."""
        response = client.post(
            "/api/v1/tickets/",
            json={"description": "A API de pagamentos está retornando erro 500."},
        )
        assert response.json()["title"] == "A API de pagamentos está retornando erro 500."

    def test_create_ticket_infers_category_financeiro(self, client):
        """A categoria deve ser inferida como Financeiro para texto de pagamento."""
        response = client.post(
            "/api/v1/tickets/",
            json={"description": "A API de pagamentos está retornando erro 500."},
        )
        assert response.json()["category"] == "Financeiro"

    def test_create_ticket_infers_priority_critica(self, client):
        """A prioridade deve ser inferida como Crítica para erro 500."""
        response = client.post(
            "/api/v1/tickets/",
            json={"description": "A API de pagamentos está retornando erro 500."},
        )
        assert response.json()["priority"] == "Crítica"

    def test_create_ticket_initial_status_aberto(self, client):
        """O status inicial de um chamado deve ser 'aberto'."""
        response = client.post(
            "/api/v1/tickets/",
            json={"description": "A API de pagamentos está retornando erro 500."},
        )
        assert response.json()["status"] == "aberto"

    def test_create_ticket_has_created_at(self, client):
        """O chamado criado deve ter created_at preenchido."""
        response = client.post(
            "/api/v1/tickets/",
            json={"description": "A API de pagamentos está retornando erro 500."},
        )
        assert response.json()["created_at"] is not None

    def test_create_ticket_has_updated_at(self, client):
        """O chamado criado deve ter updated_at preenchido."""
        response = client.post(
            "/api/v1/tickets/",
            json={"description": "A API de pagamentos está retornando erro 500."},
        )
        assert response.json()["updated_at"] is not None

    def test_create_ticket_with_explicit_category(self, client):
        """A categoria enviada manualmente deve ser mantida."""
        response = client.post(
            "/api/v1/tickets/",
            json={
                "description": "Não consigo acessar o sistema com minha senha.",
                "category": "Suporte",
            },
        )
        assert response.json()["category"] == "Suporte"

    def test_create_ticket_with_explicit_priority(self, client):
        """A prioridade enviada manualmente deve ser mantida."""
        response = client.post(
            "/api/v1/tickets/",
            json={
                "description": "Não consigo acessar o sistema com minha senha.",
                "priority": "Alta",
            },
        )
        assert response.json()["priority"] == "Alta"

    def test_create_ticket_with_explicit_title(self, client):
        """O título enviado manualmente deve ser mantido."""
        response = client.post(
            "/api/v1/tickets/",
            json={"description": "Descrição do chamado.", "title": "Meu título"},
        )
        assert response.json()["title"] == "Meu título"


class TestCreateTicketValidation:
    """Testes de validação na criação de chamados."""

    def test_create_ticket_empty_description_returns_422(self, client):
        """Descrição vazia deve retornar 422."""
        response = client.post("/api/v1/tickets/", json={"description": ""})
        assert response.status_code == 422

    def test_create_ticket_short_description_returns_422(self, client):
        """Descrição muito curta deve retornar 422."""
        response = client.post("/api/v1/tickets/", json={"description": "x"})
        assert response.status_code == 422

    def test_create_ticket_missing_description_returns_422(self, client):
        """Descrição ausente deve retornar 422."""
        response = client.post("/api/v1/tickets/", json={})
        assert response.status_code == 422

    def test_create_ticket_invalid_category_returns_422(self, client):
        """Categoria inválida deve retornar 422."""
        response = client.post(
            "/api/v1/tickets/",
            json={"description": "Descrição válida.", "category": "Inexistente"},
        )
        assert response.status_code == 422

    def test_create_ticket_invalid_priority_returns_422(self, client):
        """Prioridade inválida deve retornar 422."""
        response = client.post(
            "/api/v1/tickets/",
            json={"description": "Descrição válida.", "priority": "Extrema"},
        )
        assert response.status_code == 422