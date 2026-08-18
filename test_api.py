"""
Testes para a API de chamados (tickets).

Executa testes end-to-end usando o TestClient do FastAPI.
"""

import json

from fastapi.testclient import TestClient

from main import app
from app.db.session import Base, engine

# Recria as tabelas antes dos testes
Base.metadata.create_all(bind=engine)

client = TestClient(app)

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = ""):
    global passed, failed
    if condition:
        passed += 1
        print(f"✅ {name}")
    else:
        failed += 1
        print(f"❌ {name} — {detail}")


# ------------------------------------------------------------------
# 1. Health Check
# ------------------------------------------------------------------
print("\n=== 1. Health Check ===")

response = client.get("/")
check("GET / retorna 200", response.status_code == 200, f"Status: {response.status_code}")
check("Health check retorna status ok", response.json().get("status") == "ok", str(response.json()))


# ------------------------------------------------------------------
# 2. Criar chamado (estruturação automática)
# ------------------------------------------------------------------
print("\n=== 2. Criar chamado (estruturação automática) ===")

response = client.post(
    "/api/v1/tickets/",
    json={"description": "A API de pagamentos está retornando erro 500."},
)
check("POST /api/v1/tickets/ retorna 201", response.status_code == 201, f"Status: {response.status_code}")

ticket1 = response.json()
check("ID gerado", ticket1["id"] == 1, f"ID: {ticket1.get('id')}")
check("Descrição preservada", ticket1["description"] == "A API de pagamentos está retornando erro 500.", ticket1.get("description"))
check("Título inferido", ticket1["title"] == "A API de pagamentos está retornando erro 500.", ticket1.get("title"))
check("Categoria inferida = Financeiro", ticket1["category"] == "Financeiro", ticket1.get("category"))
check("Prioridade inferida = Crítica", ticket1["priority"] == "Crítica", ticket1.get("priority"))
check("Status inicial = aberto", ticket1["status"] == "aberto", ticket1.get("status"))
check("created_at presente", ticket1.get("created_at") is not None)
check("updated_at presente", ticket1.get("updated_at") is not None)


# ------------------------------------------------------------------
# 3. Criar chamado com dados estruturados manualmente
# ------------------------------------------------------------------
print("\n=== 3. Criar chamado com dados explícitos ===")

response = client.post(
    "/api/v1/tickets/",
    json={
        "description": "Não consigo acessar o sistema com minha senha.",
        "category": "Suporte",
        "priority": "Alta",
    },
)
check("POST retorna 201", response.status_code == 201, f"Status: {response.status_code}")

ticket2 = response.json()
check("ID = 2", ticket2["id"] == 2, f"ID: {ticket2.get('id')}")
check("Categoria manual mantida (Suporte)", ticket2["category"] == "Suporte", ticket2.get("category"))
check("Prioridade manual mantida (Alta)", ticket2["priority"] == "Alta", ticket2.get("priority"))


# ------------------------------------------------------------------
# 4. Listar chamados
# ------------------------------------------------------------------
print("\n=== 4. Listar chamados ===")

response = client.get("/api/v1/tickets/")
check("GET /api/v1/tickets/ retorna 200", response.status_code == 200, f"Status: {response.status_code}")

data = response.json()
check("Total = 2", data["total"] == 2, f"Total: {data.get('total')}")
check("Lista tem 2 itens", len(data["items"]) == 2, f"Items: {len(data.get('items', []))}")


# ------------------------------------------------------------------
# 5. Listar com filtros
# ------------------------------------------------------------------
print("\n=== 5. Listar com filtros ===")

response = client.get("/api/v1/tickets/?status=aberto")
check("Filtro por status", response.json()["total"] == 2, str(response.json()))

response = client.get("/api/v1/tickets/?category=Financeiro")
check("Filtro por categoria", response.json()["total"] == 1, str(response.json()))

response = client.get("/api/v1/tickets/?search=senha")
check("Filtro por busca", response.json()["total"] == 1, str(response.json()))


# ------------------------------------------------------------------
# 6. Buscar por ID
# ------------------------------------------------------------------
print("\n=== 6. Buscar por ID ===")

response = client.get("/api/v1/tickets/1")
check("GET /api/v1/tickets/1 retorna 200", response.status_code == 200, f"Status: {response.status_code}")
check("Ticket retornado tem id=1", response.json()["id"] == 1, str(response.json()))

response = client.get("/api/v1/tickets/999")
check("GET /api/v1/tickets/999 retorna 404", response.status_code == 404, f"Status: {response.status_code}")


# ------------------------------------------------------------------
# 7. Atualização parcial (PATCH)
# ------------------------------------------------------------------
print("\n=== 7. Atualização parcial (PATCH) ===")

response = client.patch(
    "/api/v1/tickets/1",
    json={"status": "em andamento", "priority": "Baixa"},
)
check("PATCH retorna 200", response.status_code == 200, f"Status: {response.status_code}")

data = response.json()
check("Status atualizado", data["status"] == "em andamento", str(data.get("status")))
check("Prioridade atualizada", data["priority"] == "Baixa", str(data.get("priority")))
check("Título preservado", data["title"] == "A API de pagamentos está retornando erro 500.", str(data.get("title")))


# ------------------------------------------------------------------
# 8. Atualização completa (PUT)
# ------------------------------------------------------------------
print("\n=== 8. Atualização completa (PUT) ===")

response = client.put(
    "/api/v1/tickets/2",
    json={"description": "O problema do acesso foi resolvido, obrigado pelo suporte.", "title": "Acesso restabelecido"},
)
check("PUT retorna 200", response.status_code == 200, f"Status: {response.status_code}")

data = response.json()
check("Descrição atualizada", data["description"] == "O problema do acesso foi resolvido, obrigado pelo suporte.", str(data.get("description")))
check("Título explícito usado", data["title"] == "Acesso restabelecido", str(data.get("title")))
check("Categoria re-inferida (Suporte)", data["category"] == "Suporte", str(data.get("category")))


# ------------------------------------------------------------------
# 9. Validação de campos
# ------------------------------------------------------------------
print("\n=== 9. Validação de campos ===")

response = client.post("/api/v1/tickets/", json={"description": ""})
check("Descrição vazia retorna 422", response.status_code == 422, f"Status: {response.status_code}")

response = client.post("/api/v1/tickets/", json={"description": "x"})
check("Descrição curta retorna 422", response.status_code == 422, f"Status: {response.status_code}")

response = client.patch("/api/v1/tickets/1", json={"status": "invalido"})
check("Status inválido retorna 422", response.status_code == 422, f"Status: {response.status_code}")

response = client.patch("/api/v1/tickets/1", json={"priority": "Extrema"})
check("Prioridade inválida retorna 422", response.status_code == 422, f"Status: {response.status_code}")


# ------------------------------------------------------------------
# 10. Verificar que NÃO existe DELETE
# ------------------------------------------------------------------
print("\n=== 10. Sem endpoint DELETE ===")

response = client.delete("/api/v1/tickets/1")
check("DELETE /api/v1/tickets/1 não existe (405)", response.status_code == 405, f"Status: {response.status_code}")


# ------------------------------------------------------------------
# Resumo
# ------------------------------------------------------------------
print("\n" + "=" * 50)
print(f"RESULTADO: {passed} passed, {failed} failed")
print("=" * 50)

if failed > 0:
    raise SystemExit(1)
