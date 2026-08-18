# 🎫 AI Ticket Agent API

API de chamados de suporte técnico construída com **FastAPI**.

## 🎯 Objetivo — Fase 1

Criar uma API capaz de receber um chamado em texto livre e devolvê-lo **estruturado**.

**Exemplo:**

```
Entrada:
"A API de pagamentos está retornando erro 500."

Saída estruturada:
{
  "id": 1,
  "title": "A API de pagamentos está retornando erro 500.",
  "description": "A API de pagamentos está retornando erro 500.",
  "category": "Financeiro",
  "priority": "Crítica",
  "status": "aberto",
  "created_at": "2026-08-17T19:40:00.000000+00:00",
  "updated_at": "2026-08-17T19:40:00.000000+00:00"
}
```

## 🛠️ Tecnologias

| Tecnologia     | Versão   | Propósito                     |
|----------------|----------|-------------------------------|
| Python         | 3.14+    | Linguagem principal           |
| FastAPI        | 0.115+   | Framework web                 |
| Uvicorn        | 0.34+    | Servidor ASGI                 |
| SQLAlchemy     | 2.0+     | ORM para banco de dados       |
| Pydantic       | 2.12+    | Validação e serialização      |
| pytest         | 8.0+     | Testes automatizados          |

> **Nota sobre o banco:** por padrão, a API usa **SQLite em memória**
> (`sqlite://`), que zera os dados ao reiniciar. Para usar outro banco,
> defina `DATABASE_URL` no arquivo `.env` (veja `.env.example`).

## 📂 Estrutura do Projeto

```
ai-ticket-agent/
├── main.py                 # Ponto de entrada (FastAPI app)
├── requirements.txt        # Dependências Python
├── pytest.ini              # Configuração do pytest
├── .env.example            # Variáveis de ambiente de exemplo
├── README.md               # Documentação do projeto
├── AGENTS.md               # Guia para agentes de IA
├── PRD.md                  # Documento de requisitos do produto
├── test_api.py             # Testes rápidos (script único, legado)
├── app/
│   ├── __init__.py
│   ├── crud.py             # Operações de banco de dados
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py       # Configurações (Pydantic Settings)
│   │   └── constants.py    # Constantes de domínio (categorias, prioridades, status)
│   ├── db/
│   │   ├── __init__.py
│   │   └── session.py      # Engine, SessionLocal, Base
│   ├── models/
│   │   ├── __init__.py
│   │   └── ticket.py       # Modelo ORM Ticket
│   ├── routers/
│   │   ├── __init__.py
│   │   └── tickets.py      # Rotas da API de tickets
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── ticket.py       # Schemas Pydantic de Ticket
│   └── services/
│       ├── __init__.py
│       ├── classifier.py        # TicketClassifier (wrapper)
│       ├── classifier_service.py # Serviço de classificação (API pública)
│       └── structuring.py       # TicketStructuringService (heurísticas)
└── tests/
    ├── __init__.py
    ├── conftest.py         # Fixtures compartilhadas
    ├── test_health.py      # Testes do health check
    ├── test_models.py      # Testes do modelo ORM
    ├── test_schemas.py     # Testes dos schemas Pydantic
    ├── test_services.py    # Testes dos serviços
    ├── test_tickets_create.py  # Testes de criação
    ├── test_tickets_list.py    # Testes de listagem
    └── test_tickets_crud.py    # Testes de CRUD
```

## 🚀 Como Executar

### 1. Instalar dependências

```bash
python -m pip install -r requirements.txt
```

### 2. Iniciar o servidor

```bash
python -m uvicorn main:app --reload
```

Ou:

```bash
python main.py
```

A API estará disponível em: **http://localhost:8000**

### 3. Acessar a documentação interativa

| Documentação   | URL                              |
|----------------|----------------------------------|
| Swagger UI     | http://localhost:8000/docs       |
| ReDoc          | http://localhost:8000/redoc      |

## 🔌 Endpoints da API

### Health Check

| Método | Rota        | Descrição                    |
|--------|-------------|------------------------------|
| GET    | `/`         | Status da API                |

### Tickets (CRUD sem DELETE)

| Método | Rota                  | Descrição                                             |
|--------|-----------------------|-------------------------------------------------------|
| POST   | `/api/v1/tickets/`    | Cria um novo chamado, estruturando automaticamente    |
| GET    | `/api/v1/tickets/`    | Lista chamados (filtros e paginação)                  |
| GET    | `/api/v1/tickets/{id}`| Busca um chamado por ID                              |
| PUT    | `/api/v1/tickets/{id}`| Atualiza todos os campos do chamado                   |
| PATCH  | `/api/v1/tickets/{id}`| Atualiza apenas os campos informados                  |

> ✋ **DELETE não foi criado**, conforme requisito.

### Filtros de listagem

| Parâmetro | Tipo   | Descrição                                    |
|-----------|--------|----------------------------------------------|
| `skip`    | int    | Quantidade a pular (default: 0, min: 0)      |
| `limit`   | int    | Máximo de registros (default: 100, max: 500) |
| `status`  | string | Filtrar por status                           |
| `category`| string | Filtrar por categoria                        |
| `search`  | string | Busca no título e descrição                  |

## 📝 Exemplos de Uso

### Criar um chamado (estruturação automática)

```bash
curl -X POST http://localhost:8000/api/v1/tickets/ \
  -H "Content-Type: application/json" \
  -d '{"description": "A API de pagamentos está retornando erro 500."}'
```

**Resposta (201):**

```json
{
  "id": 1,
  "title": "A API de pagamentos está retornando erro 500.",
  "description": "A API de pagamentos está retornando erro 500.",
  "category": "Financeiro",
  "priority": "Crítica",
  "status": "aberto",
  "created_at": "2026-08-17T19:40:00.000000+00:00",
  "updated_at": "2026-08-17T19:40:00.000000+00:00"
}
```

### Criar chamado já estruturado

```bash
curl -X POST http://localhost:8000/api/v1/tickets/ \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Não consigo acessar o sistema com minha senha",
    "category": "Suporte",
    "priority": "Alta"
  }'
```

### Listar chamados com filtros

```bash
curl "http://localhost:8000/api/v1/tickets/?status=aberto&category=Financeiro&search=API"
```

### Buscar por ID

```bash
curl http://localhost:8000/api/v1/tickets/1
```

### Atualização parcial

```bash
curl -X PATCH http://localhost:8000/api/v1/tickets/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "em andamento"}'
```

### Atualização completa

```bash
curl -X PUT http://localhost:8000/api/v1/tickets/1 \
  -H "Content-Type: application/json" \
  -d '{"description": "O problema foi resolvido, obrigado.", "title": "Chamado resolvido"}'
```

## 🧪 Testes

### Testes pytest (padrão)

```bash
# Todos os testes
python -m pytest

# Com saída detalhada
python -m pytest -v

# Testes específicos
python -m pytest tests/test_schemas.py
```

### Script de testes legado

```bash
python test_api.py
```

## 🔄 Como o chamado é estruturado

O serviço `TicketStructuringService` analisa o texto do chamado e infere:

| Campo      | Lógica                                                                 |
|------------|------------------------------------------------------------------------|
| **title**  | Primeiras 10 palavras da descrição (ou texto completo se menor)        |
| **category**| Palavras-chave no texto (erro, pagamento, servidor, senha, etc.)       |
| **priority**| Palavras-chave de severidade (urgente, crítico, fora do ar, etc.)      |
| **status** | Sempre iniciado como `aberto`                                          |

### Categorias reconhecidas

- `Bug` 🐛
- `Suporte` 🎧
- `Melhoria` 🚀
- `Financeiro` 💰
- `Infraestrutura` ☁️
- `Outro`

### Prioridades reconhecidas

- `Baixa`
- `Média`
- `Alta`
- `Crítica`

## 📄 Documentação Adicional

| Documento     | Descrição                                          |
|---------------|----------------------------------------------------|
| `PRD.md`      | Requisitos do produto (Product Requirements Document) |
| `AGENTS.md`   | Guia para agentes de IA trabalharem neste projeto  |
| `.env.example`| Exemplo de variáveis de ambiente                   |

## 🏗️ Próximas Fases (Roadmap)

- **Fase 2:** Classificação automática com IA
- **Fase 3:** Encaminhamento inteligente para equipes
- **Fase 4:** Relatórios e dashboards
- **Fase 5:** Notificações em tempo real

---

Desenvolvido com 💙 para o projeto **AI Ticket Agent**.