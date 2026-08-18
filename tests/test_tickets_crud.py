"""
Testes de CRUD de tickets (buscar por ID, atualizar, sem DELETE).
"""


def _create_ticket(client, description: str, **kwargs):
    """Helper para criar um ticket."""
    payload = {"description": description, **kwargs}
    return client.post("/api/v1/tickets/", json=payload)


class TestGetTicketById:
    """Testes de busca de chamado por ID."""

    def test_get_ticket_returns_200(self, client):
        """Buscar um chamado existente deve retornar 200."""
        _create_ticket(client, "A API de pagamentos está retornando erro 500.")
        response = client.get("/api/v1/tickets/1")
        assert response.status_code == 200

    def test_get_ticket_returns_correct_id(self, client):
        """O chamado retornado deve ter o ID correto."""
        _create_ticket(client, "A API de pagamentos está retornando erro 500.")
        response = client.get("/api/v1/tickets/1")
        assert response.json()["id"] == 1

    def test_get_ticket_not_found_returns_404(self, client):
        """Buscar um chamado inexistente deve retornar 404."""
        response = client.get("/api/v1/tickets/999")
        assert response.status_code == 404

    def test_get_ticket_not_found_message(self, client):
        """A mensagem de erro deve ser informativa."""
        response = client.get("/api/v1/tickets/999")
        assert "999" in response.json()["detail"]


class TestUpdateTicketPartial:
    """Testes de atualização parcial (PATCH)."""

    def test_patch_returns_200(self, client):
        """PATCH em chamado existente deve retornar 200."""
        _create_ticket(client, "A API de pagamentos está retornando erro 500.")
        response = client.patch("/api/v1/tickets/1", json={"status": "em andamento"})
        assert response.status_code == 200

    def test_patch_updates_status(self, client):
        """PATCH deve atualizar o status."""
        _create_ticket(client, "A API de pagamentos está retornando erro 500.")
        response = client.patch("/api/v1/tickets/1", json={"status": "em andamento"})
        assert response.json()["status"] == "em andamento"

    def test_patch_updates_priority(self, client):
        """PATCH deve atualizar a prioridade."""
        _create_ticket(client, "A API de pagamentos está retornando erro 500.")
        response = client.patch("/api/v1/tickets/1", json={"priority": "Baixa"})
        assert response.json()["priority"] == "Baixa"

    def test_patch_updates_category(self, client):
        """PATCH deve atualizar a categoria."""
        _create_ticket(client, "A API de pagamentos está retornando erro 500.")
        response = client.patch("/api/v1/tickets/1", json={"category": "Suporte"})
        assert response.json()["category"] == "Suporte"

    def test_patch_preserves_untouched_fields(self, client):
        """PATCH deve preservar os campos não informados."""
        _create_ticket(client, "A API de pagamentos está retornando erro 500.")
        response = client.patch("/api/v1/tickets/1", json={"status": "em andamento"})

        data = response.json()
        assert data["title"] == "A API de pagamentos está retornando erro 500."
        assert data["description"] == "A API de pagamentos está retornando erro 500."
        assert data["category"] == "Financeiro"
        assert data["priority"] == "Crítica"

    def test_patch_not_found_returns_404(self, client):
        """PATCH em chamado inexistente deve retornar 404."""
        response = client.patch("/api/v1/tickets/999", json={"status": "fechado"})
        assert response.status_code == 404

    def test_patch_invalid_status_returns_422(self, client):
        """PATCH com status inválido deve retornar 422."""
        _create_ticket(client, "A API de pagamentos está retornando erro 500.")
        response = client.patch("/api/v1/tickets/1", json={"status": "invalido"})
        assert response.status_code == 422

    def test_patch_invalid_priority_returns_422(self, client):
        """PATCH com prioridade inválida deve retornar 422."""
        _create_ticket(client, "A API de pagamentos está retornando erro 500.")
        response = client.patch("/api/v1/tickets/1", json={"priority": "Extrema"})
        assert response.status_code == 422


class TestUpdateTicketFull:
    """Testes de atualização completa (PUT)."""

    def test_put_returns_200(self, client):
        """PUT em chamado existente deve retornar 200."""
        _create_ticket(client, "A API de pagamentos está retornando erro 500.")
        response = client.put(
            "/api/v1/tickets/1",
            json={"description": "Nova descrição completa."},
        )
        assert response.status_code == 200

    def test_put_updates_description(self, client):
        """PUT deve substituir a descrição."""
        _create_ticket(client, "A API de pagamentos está retornando erro 500.")
        response = client.put(
            "/api/v1/tickets/1",
            json={"description": "Nova descrição completa."},
        )
        assert response.json()["description"] == "Nova descrição completa."

    def test_put_uses_explicit_title(self, client):
        """PUT com título explícito deve usá-lo."""
        _create_ticket(client, "A API de pagamentos está retornando erro 500.")
        response = client.put(
            "/api/v1/tickets/1",
            json={
                "description": "Nova descrição completa.",
                "title": "Novo título",
            },
        )
        assert response.json()["title"] == "Novo título"

    def test_put_reinfers_category(self, client):
        """PUT deve re-inferir a categoria a partir da nova descrição."""
        _create_ticket(client, "A API de pagamentos está retornando erro 500.")
        response = client.put(
            "/api/v1/tickets/1",
            json={"description": "O servidor está fora do ar."},
        )
        assert response.json()["category"] == "Infraestrutura"

    def test_put_preserves_status(self, client):
        """PUT deve preservar o status existente."""
        _create_ticket(client, "A API de pagamentos está retornando erro 500.")
        response = client.put(
            "/api/v1/tickets/1",
            json={"description": "Nova descrição completa."},
        )
        assert response.json()["status"] == "aberto"

    def test_put_not_found_returns_404(self, client):
        """PUT em chamado inexistente deve retornar 404."""
        response = client.put(
            "/api/v1/tickets/999",
            json={"description": "Descrição qualquer."},
        )
        assert response.status_code == 404


class TestNoDeleteEndpoint:
    """Testes de ausência do endpoint DELETE."""

    def test_delete_ticket_returns_405(self, client):
        """DELETE não deve existir (retorna 405)."""
        _create_ticket(client, "A API de pagamentos está retornando erro 500.")
        response = client.delete("/api/v1/tickets/1")
        assert response.status_code == 405