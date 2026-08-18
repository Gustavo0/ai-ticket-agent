"""
Testes do endpoint de health check.
"""


def test_health_check_returns_200(client):
    """O endpoint GET / deve retornar status 200."""
    response = client.get("/")
    assert response.status_code == 200


def test_health_check_returns_ok_status(client):
    """O health check deve retornar status 'ok'."""
    response = client.get("/")
    assert response.json()["status"] == "ok"


def test_health_check_returns_service_name(client):
    """O health check deve retornar o nome do serviço."""
    response = client.get("/")
    assert response.json()["service"] == "AI Ticket Agent API"


def test_health_check_returns_version(client):
    """O health check deve retornar a versão da aplicação."""
    response = client.get("/")
    assert response.json()["version"] == "0.2.0"