"""
Rotas da API de chamados (tickets).

CRUD padrão sem DELETE, conforme requisito:

- POST   /tickets/          → Criar chamado (estrutura automaticamente)
- GET    /tickets/          → Listar chamados (com filtros e paginação)
- GET    /tickets/{id}      → Buscar chamado por ID
- PUT    /tickets/{id}      → Atualizar chamado (substitui todos os campos)
- PATCH  /tickets/{id}      → Atualização parcial (campos informados)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db.session import get_db
from app.models import Ticket
from app.services import TicketStructuringService

router = APIRouter(prefix="/tickets", tags=["tickets"])

structuring_service = TicketStructuringService()


@router.post(
    "/",
    response_model=schemas.TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar um novo chamado",
    description=(
        "Recebe um chamado em texto livre e o devolve estruturado.\n\n"
        "**Exemplo:**\n"
        '```json\n'
        '{"description": "A API de pagamentos está retornando erro 500."}\n'
        '```\n\n'
        "O serviço infere automaticamente título, categoria e prioridade."
    ),
)
def create_ticket(payload: schemas.TicketCreate, db: Session = Depends(get_db)):
    """
    Fase 1 — Criar a API de chamados.

    Recebe um chamado textual e o devolve estruturado.
    """
    # Estrutura o chamado: infere título, categoria e prioridade
    structured = structuring_service.structure(payload.description)

    ticket = Ticket(
        title=payload.title or structured["title"],
        description=payload.description,
        category=payload.category or structured["category"],
        priority=payload.priority or structured["priority"],
        status="aberto",
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


@router.get(
    "/",
    response_model=schemas.TicketListResponse,
    summary="Listar chamados",
    description="Lista todos os chamados com paginação e filtros opcionais.",
)
def list_tickets(
    skip: int = Query(0, ge=0, description="Quantidade de registros a pular"),
    limit: int = Query(100, ge=1, le=500, description="Quantidade máxima de registros"),
    status_filter: str | None = Query(None, alias="status", description="Filtrar por status"),
    category: str | None = Query(None, description="Filtrar por categoria"),
    search: str | None = Query(None, description="Buscar por texto no título ou descrição"),
    db: Session = Depends(get_db),
):
    tickets, total = crud.get_tickets(
        db=db,
        skip=skip,
        limit=limit,
        status=status_filter,
        category=category,
        search=search,
    )

    items = [schemas.TicketResponse.model_validate(t) for t in tickets]

    return schemas.TicketListResponse(total=total, items=items)


@router.get(
    "/{ticket_id}",
    response_model=schemas.TicketResponse,
    summary="Buscar chamado por ID",
)
def get_ticket_by_id(ticket_id: int, db: Session = Depends(get_db)):
    ticket = crud.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chamado com ID {ticket_id} não encontrado.",
        )
    return ticket


@router.put(
    "/{ticket_id}",
    response_model=schemas.TicketResponse,
    summary="Atualizar chamado (substitui todos os campos)",
)
def update_ticket_full(
    ticket_id: int,
    payload: schemas.TicketCreate,
    db: Session = Depends(get_db),
):
    """Atualização completa: todos os campos são substituídos pelos informados."""
    ticket = crud.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chamado com ID {ticket_id} não encontrado.",
        )

    structured = structuring_service.structure(payload.description)

    ticket.title = payload.title or structured["title"]
    ticket.description = payload.description
    ticket.category = payload.category or structured["category"]
    ticket.priority = payload.priority or structured["priority"]

    db.commit()
    db.refresh(ticket)
    return ticket


@router.patch(
    "/{ticket_id}",
    response_model=schemas.TicketResponse,
    summary="Atualizar chamado parcialmente (só campos informados)",
)
def update_ticket_partial(
    ticket_id: int,
    payload: schemas.TicketUpdate,
    db: Session = Depends(get_db),
):
    ticket = crud.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chamado com ID {ticket_id} não encontrado.",
        )

    updated_ticket = crud.update_ticket(db, ticket, payload)
    return updated_ticket