"""
Testes do endpoint de listagem de tickets (GET /api/v1/tickets/).
"""


def _create_ticket(client, description: str, **kwargs):
    """Helper para criar um ticket."""
    payload = {"description": description, **kwargs}
    return client.post("/api/v1/tickets/", json=payload)


class TestListTickets:
    """Testes de listagem de chamados."""

    def test_list_tickets_returns_200(self, client):
        """Listar chamados deve retornar status 200."""
        response = client.get("/api/v1/tickets/")
        assert response.status_code == 200

    def test_list_tickets_empty(self, client):
        """Listar chamados sem registros deve retornar total 0."""
        response = client.get("/api/v1/tickets/")
        assert response.json()["total"] == 0
        assert response.json()["items"] == []

    def test_list_tickets_returns_total(self, client):
        """Listar chamados deve retornar o total correto."""
        _create_ticket(client, "A API de pagamentos está retornando erro 500.")
        _create_ticket(client, "Não consigo acessar o sistema com minha senha.")

        response = client.get("/api/v1/tickets/")
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_list_tickets_most_recent_first(self, client):
        """Listar chamados deve retornar os mais recentes primeiro."""
        _create_ticket(client, "Primeiro chamado.")
        _create_ticket(client, "Segundo chamado.")

        response = client.get("/api/v1/tickets/")
        items = response.json()["items"]
        assert items[0]["description"] == "Segundo chamado."
        assert items[1]["description"] == "Primeiro chamado."


class TestListTicketsFilters:
    """Testes de filtros na listagem de chamados."""

    def _setup_tickets(self, client):
        _create_ticket(client, "A API de pagamentos está retornando erro 500.")
        _create_ticket(client, "Não consigo acessar o sistema com minha senha.")
        _create_ticket(client, "O servidor está fora do ar.")

    def test_filter_by_status(self, client):
        """Filtrar por status deve retornar apenas chamados com aquele status."""
        self._setup_tickets(client)

        response = client.get("/api/v1/tickets/?status=aberto")
        assert response.json()["total"] == 3

    def test_filter_by_status_fechado(self, client):
        """Filtrar por status fechado não deve retornar chamados abertos."""
        self._setup_tickets(client)
        client.patch("/api/v1/tickets/1", json={"status": "fechado"})

        response = client.get("/api/v1/tickets/?status=fechado")
        assert response.json()["total"] == 1

    def test_filter_by_category(self, client):
        """Filtrar por categoria deve retornar apenas chamados daquela categoria."""
        self._setup_tickets(client)

        response = client.get("/api/v1/tickets/?category=Financeiro")
        assert response.json()["total"] == 1
        assert response.json()["items"][0]["category"] == "Financeiro"

    def test_filter_by_category_case_insensitive(self, client):
        """Filtrar por categoria deve ser case-insensitive."""
        self._setup_tickets(client)

        response = client.get("/api/v1/tickets/?category=financeiro")
        assert response.json()["total"] == 1

    def test_filter_by_search(self, client):
        """Buscar por texto deve retornar chamados que contenham o termo."""
        self._setup_tickets(client)

        response = client.get("/api/v1/tickets/?search=senha")
        assert response.json()["total"] == 1

    def test_filter_by_search_in_title(self, client):
        """Buscar deve encontrar termos no título."""
        self._setup_tickets(client)

        response = client.get("/api/v1/tickets/?search=API")
        assert response.json()["total"] == 1


class TestListTicketsPagination:
    """Testes de paginação na listagem de chamados."""

    def test_pagination_skip(self, client):
        """skip deve pular os primeiros registros."""
        _create_ticket(client, "Primeiro chamado.")
        _create_ticket(client, "Segundo chamado.")
        _create_ticket(client, "Terceiro chamado.")

        response = client.get("/api/v1/tickets/?skip=1")
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 2
        assert data["items"][0]["description"] == "Segundo chamado."

    def test_pagination_limit(self, client):
        """limit deve limitar a quantidade de registros retornados."""
        _create_ticket(client, "Primeiro chamado.")
        _create_ticket(client, "Segundo chamado.")
        _create_ticket(client, "Terceiro chamado.")

        response = client.get("/api/v1/tickets/?limit=2")
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 2

    def test_pagination_invalid_skip_returns_422(self, client):
        """skip negativo deve retornar 422."""
        response = client.get("/api/v1/tickets/?skip=-1")
        assert response.status_code == 422

    def test_pagination_invalid_limit_returns_422(self, client):
        """limit zero ou negativo deve retornar 422."""
        response = client.get("/api/v1/tickets/?limit=0")
        assert response.status_code == 422