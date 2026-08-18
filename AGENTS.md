# AGENTS.md — Guia para Agentes de IA

Este documento orienta agentes de IA (e desenvolvedores) a trabalharem
de forma eficiente neste projeto.

## Visão Geral

**AI Ticket Agent API** é uma API REST construída com **FastAPI** que recebe
chamados de suporte técnico em texto livre e os devolve estruturados
(com título, categoria, prioridade e status).

O projeto está na **Fase 1**: API de criação e gestão de chamados com
**estruturação automática** baseada em heurísticas de palavras-chave.

## Stack Tecnológica

| Camada       | Tecnologia                | Propósito                          |
|--------------|---------------------------|------------------------------------|
| Linguagem    | Python 3.14+              | Linguagem principal                |
| Framework    | FastAPI                   | API REST + documentação automática |
| Servidor     | Uvicorn                   | Servidor ASGI                      |
| ORM          | SQLAlchemy 2.x            | Mapeamento objeto-relacional       |
| Validação    | Pydantic v2               | Schemas e validação de dados       |
| Banco        | SQLite em memória (padrão)| Banco de dados em memória          |
| Testes       | pytest                    | Suite de testes automatizados      |

## Estrutura do Projeto

```
ai-ticket-agent/
├── main.py                 # Ponto de entrada (FastAPI app)
├── requirements.txt        # Dependências Python
├── pytest.ini              # Configuração do pytest
├── .env.example            # Variáveis de ambiente de exemplo
├── README.md               # Documentação do projeto
├── AGENTS.md               # Este guia para agentes de IA
├── PRD.md                  # Documento de requisitos do produto
├── test_api.py             # Testes rápidos (script único, legado)
└── app/
    ├── __init__.py
    ├── crud.py             # Operações de banco de dados
    ├── core/
    │   ├── __init__.py
    │   ├── config.py       # Configurações (Pydantic Settings)
    │   └── constants.py    # Constantes de domínio (categorias, prioridades, status)
    ├── db/
    │   ├── __init__.py
    │   └── session.py      # Engine, SessionLocal, Base
    ├── models/
    │   ├── __init__.py
    │   └── ticket.py       # Modelo ORM Ticket
    ├── routers/
    │   ├── __init__.py
    │   └── tickets.py      # Rotas da API de tickets
    ├── schemas/
    │   ├── __init__.py
    │   └── ticket.py       # Schemas Pydantic de Ticket
    └── services/
        ├── __init__.py
        ├── classifier.py        # TicketClassifier (wrapper)
        ├── classifier_service.py # Serviço de classificação (API pública)
        └── structuring.py       # TicketStructuringService (heurísticas)
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

## Camadas da Aplicação

O projeto segue uma arquitetura em camadas:

```
┌─────────────────────────────────────────────────────┐
│  Cliente (HTTP)                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │  routers/tickets.py  (camada de API)          │  │
│  └───────────────────────────────────────────────┘  │
│                     │                               │
│                     ▼                               │
│  ┌───────────────────────────────────────────────┐  │
│  │  schemas/ticket.py  (Pydantic - validação)    │  │
│  └───────────────────────────────────────────────┘  │
│                     │                               │
│                     ▼                               │
│  ┌───────────────────────────────────────────────┐  │
│  │  services/  (lógica de negócio)               │  │
│  │  └── structuring.py  (estruturação automática)│  │
│  └───────────────────────────────────────────────┘  │
│                     │                               │
│                     ▼                               │
│  ┌───────────────────────────────────────────────┐  │
│  │  crud.py  (operações de banco)                │  │
│  │  models/ticket.py  (ORM)                      │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Regras de Arquitetura

1. **Routers** (camada de API) — só HTTP e validação. Nenhuma lógica de negócio.
2. **Schemas** — validação e serialização. Não devem importar de `models`.
3. **Services** — lógica de negócio (estruturação, classificação).
4. **CRUD** — operações de banco de dados. Não deve conter regras de negócio.
5. **Models** — definem as tabelas do banco. Não devem importar de `schemas`.

## Comandos Essenciais

### Instalar dependências

```bash
python -m pip install -r requirements.txt
```

### Rodar o servidor

```bash
python main.py
# ou
python -m uvicorn main:app --reload
```

### Rodar os testes

```bash
# Todos os testes pytest
python -m pytest

# Testes específicos
python -m pytest tests/test_schemas.py

# Com cobertura de saída detalhada
python -m pytest -v

# Script de testes legado (rápido, sem pytest)
python test_api.py
```

### Verificar importações

```bash
python -c "from main import app; print('OK')"
```

## Endpoints da API

| Método | Rota                     | Descrição                                   |
|--------|--------------------------|---------------------------------------------|
| GET    | `/`                      | Health check                                |
| POST   | `/api/v1/tickets/`       | Criar chamado (estruturação automática)     |
| GET    | `/api/v1/tickets/`       | Listar chamados (filtros + paginação)       |
| GET    | `/api/v1/tickets/{id}`   | Buscar chamado por ID                       |
| PUT    | `/api/v1/tickets/{id}`   | Atualização completa (substitui campos)     |
| PATCH  | `/api/v1/tickets/{id}`   | Atualização parcial (só campos informados)  |

> **Importante:** Não existe endpoint DELETE, conforme requisito do produto.

### Filtros de listagem

| Parâmetro | Tipo   | Descrição                                    |
|-----------|--------|----------------------------------------------|
| `skip`    | int    | Quantidade a pular (default: 0, min: 0)      |
| `limit`   | int    | Máximo de registros (default: 100, max: 500) |
| `status`  | string | Filtrar por status                           |
| `category`| string | Filtrar por categoria                        |
| `search`  | string | Busca no título e descrição                  |

## Valores Válidos (Domínio)

### Categorias

| Valor          | Alias (normalização) |
|----------------|----------------------|
| `Bug`          | bug                  |
| `Suporte`      | suporte              |
| `Melhoria`     | melhoria             |
| `Financeiro`   | financeiro           |
| `Infraestrutura`| infraestrutura       |
| `Outro`        | outro                |

### Prioridades

| Valor      | Alias (normalização) |
|------------|----------------------|
| `Baixa`    | baixa                |
| `Média`    | media, média         |
| `Alta`     | alta                 |
| `Crítica`  | critica, crítica     |

### Status

| Valor          |
|----------------|
| `aberto`       |
| `em andamento` |
| `resolvido`    |
| `fechado`      |

> As constantes desses valores estão em `app/core/constants.py`.

## Regras de Negócio

1. **Estruturação automática**: Ao criar um chamado sem `title`, `category`
   ou `priority`, o serviço `TicketStructuringService` infere esses campos
   a partir da descrição usando palavras-chave ponderadas.
2. **Status inicial**: Todo chamado novo começa com status `aberto`.
3. **Sem DELETE**: Não criar endpoint de exclusão.
4. **Valores canônicos**: Categorias e prioridades são normalizadas para o
   formato canônico (ex: `"media"` → `"Média"`).
5. **Validação**: A descrição é obrigatória (mínimo 3, máximo 5000 caracteres).
   O título é opcional (máximo 200).
6. **Paginação**: A listagem retorna no máximo 500 registros por página.

## Como Contribuir

1. Crie uma branch a partir de `main`.
2. Siga a arquitetura em camadas descrita acima.
3. Adicione testes para toda nova funcionalidade.
4. Execute `python -m pytest` antes de abrir um PR (todos devem passar).
5. Mantenha o README e o PRD atualizados.

## Boas Práticas para Agentes de IA

### Antes de Editar

1. Leia `app/core/constants.py` para entender os valores válidos.
2. Leia `app/schemas/ticket.py` para entender a validação.
3. Leia `app/services/structuring.py` para entender as heurísticas.
4. Verifique se o padrão que você vai alterar é usado em outras camadas.

### Ao Adicionar Funcionalidades

1. **Constantes** → `app/core/constants.py`
2. **Modelo** → `app/models/`
3. **Schema** → `app/schemas/`
4. **Serviço** → `app/services/`
5. **Operações de banco** → `app/crud.py`
6. **Rota** → `app/routers/`
7. **Testes** → `tests/`

### Ao Corrigir Bugs

1. Reproduza o bug com um teste que falhe.
2. Corrija o código.
3. Execute `python -m pytest` — todos os testes devem passar.

### Erros Comuns

- **Não usar `PRIORITY_ALIASES`**: Importe de `app.core.constants` e use
  `PRIORITY_ALIASES` para normalizar "media" → "Média", "critica" → "Crítica".
- **Não esquecer os aliases de categoria**: `_normalize_category` já faz a
  normalização via `VALID_CATEGORIES`.
- **Fazer importações circulares**: `models` não deve importar de `schemas`,
  e `schemas` não deve importar de `models`.