# PRD — Product Requirements Document

## AI Ticket Agent API

### 1. Visão Geral

**Objetivo:** Receber chamados de suporte técnico em texto livre e devolvê-los
estruturados, com título, categoria, prioridade e status — sem intervenção manual.

**Fase atual:** Fase 1 — CRUD de chamados com estruturação automática baseada em
heurísticas de palavras-chave.

### 2. Problema

Os chamados de suporte chegam em texto livre, o que dificulta:

- **Priorização** — não é possível saber rapidamente quais chamados são urgentes.
- **Roteamento** — não há categoria definida para encaminhar à equipe correta.
- **Métricas** — não há dados estruturados para gerar relatórios.

### 3. Solução Proposta

Uma API REST que:

1. Recebe um chamado em texto livre via `POST /api/v1/tickets/`.
2. Estrutura automaticamente o chamado:
   - **Título** — gerado a partir da descrição (primeiras 10 palavras).
   - **Categoria** — inferida por palavras-chave ponderadas.
   - **Prioridade** — inferida por palavras-chave de severidade.
   - **Status** — sempre inicia como `aberto`.
3. Disponibiliza CRUD completo (sem DELETE) para gestão dos chamados.

### 4. Personas

| Persona        | Descrição                                           |
|----------------|-----------------------------------------------------|
| Usuário final  | Abre chamados de suporte em texto livre.            |
| Analista       | Consulta, filtra e atualiza chamados.               |
| Gestor         | Acompanha métricas e relatórios (fases futuras).    |

### 5. Requisitos Funcionais

#### RF-01: Health Check

| ID   | Requisito                                              |
|------|--------------------------------------------------------|
| RF-01| Fornecer um endpoint `GET /` que retorna o status da API. |

#### RF-02: Criar Chamado

| ID   | Requisito                                                                  |
|------|----------------------------------------------------------------------------|
| RF-02| `POST /api/v1/tickets/` recebe um chamado em texto livre e devolve estruturado. |
| RF-02.1| Se `title`, `category` ou `priority` não forem informados, inferi-los da descrição. |
| RF-02.2| `description` é obrigatória (mínimo 3, máximo 5000 caracteres).            |
| RF-02.3| `title` é opcional (máximo 200 caracteres).                                 |
| RF-02.4| O status inicial de todo chamado é `aberto`.                               |
| RF-02.5| Categorias e prioridades são normalizadas para o formato canônico.         |

#### RF-03: Listar Chamados

| ID   | Requisito                                                                  |
|------|----------------------------------------------------------------------------|
| RF-03| `GET /api/v1/tickets/` lista chamados com paginação e filtros.             |
| RF-03.1| Filtros: `status`, `category`, `search` (título e descrição).             |
| RF-03.2| Paginação: `skip` (default 0) e `limit` (default 100, máximo 500).        |
| RF-03.3| Ordenação: mais recentes primeiro.                                         |

#### RF-04: Buscar Chamado por ID

| ID   | Requisito                                                      |
|------|----------------------------------------------------------------|
| RF-04| `GET /api/v1/tickets/{id}` retorna um chamado específico.      |
| RF-04.1| Retornar 404 se o chamado não existir.                         |

#### RF-05: Atualizar Chamado

| ID   | Requisito                                                                  |
|------|----------------------------------------------------------------------------|
| RF-05| `PUT /api/v1/tickets/{id}` substitui todos os campos do chamado.           |
| RF-05.1| `PATCH /api/v1/tickets/{id}` atualiza apenas os campos informados.         |
| RF-05.2| Retornar 404 se o chamado não existir.                                     |

#### RF-06: Sem DELETE

| ID   | Requisito                                             |
|------|-------------------------------------------------------|
| RF-06| **Não** existe endpoint DELETE. Chamados nunca são excluídos. |

### 6. Requisitos Não-Funcionais

| ID    | Requisito                                                        |
|-------|------------------------------------------------------------------|
| RNF-01| Banco de dados em memória (SQLite) — dados zerados ao reiniciar. |
| RNF-02| Validação de dados com Pydantic v2.                              |
| RNF-03| Documentação automática via Swagger UI (`/docs`) e ReDoc (`/redoc`). |
| RNF-04| Testes automatizados com pytest.                                 |
| RNF-05| Arquitetura em camadas: routers → schemas → services → crud → models. |
| RNF-06| Configuração via variáveis de ambiente (Pydantic Settings).      |

### 7. Regras de Negócio

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

### 8. Valores Válidos de Domínio

#### Categorias

| Valor          | Alias (normalização) |
|----------------|----------------------|
| `Bug`          | bug                  |
| `Suporte`      | suporte              |
| `Melhoria`     | melhoria             |
| `Financeiro`   | financeiro           |
| `Infraestrutura`| infraestrutura       |
| `Outro`        | outro                |

#### Prioridades

| Valor      | Alias (normalização) |
|------------|----------------------|
| `Baixa`    | baixa                |
| `Média`    | media, média         |
| `Alta`     | alta                 |
| `Crítica`  | critica, crítica     |

#### Status

| Valor          |
|----------------|
| `aberto`       |
| `em andamento` |
| `resolvido`    |
| `fechado`      |

### 9. Heurísticas de Estruturação

#### Categorias (palavras-chave ponderadas)

| Categoria       | Exemplos de palavras-chave                          |
|-----------------|-----------------------------------------------------|
| `Bug`           | erro, bug, exception, crash, falha, não funciona    |
| `Suporte`       | ajuda, senha, login, acesso, não consigo, dúvida    |
| `Melhoria`      | sugestão, melhorar, seria bom, feature, otimizar    |
| `Financeiro`    | pagamento, fatura, boleto, cartão, reembolso, pix   |
| `Infraestrutura`| servidor, rede, banco, disco, memória, down, ssl    |

#### Prioridades (palavras-chave ponderadas)

| Prioridade | Exemplos de palavras-chave                          |
|------------|-----------------------------------------------------|
| `Crítica`  | urgente, fora do ar, emergência, crash, dados perdidos |
| `Alta`     | bloqueado, parado, não funciona, impedindo          |
| `Média`    | intermitente, alguns usuários, relatório            |
| `Baixa`    | cosmético, melhoria, sugestão, quando puder         |

### 10. Métricas de Sucesso (Fase 1)

- 100% dos testes pytest passando.
- API documentada automaticamente em `/docs`.
- Chamados estruturados com categoria e prioridade sempre que possível.

### 11. Próximas Fases (Roadmap)

| Fase | Descrição                                        |
|------|--------------------------------------------------|
| 2    | Classificação automática com IA                  |
| 3    | Encaminhamento inteligente para equipes          |
| 4    | Relatórios e dashboards                          |
| 5    | Notificações em tempo real                       |