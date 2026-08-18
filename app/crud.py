"""
Operações CRUD para a tabela de tickets.
"""

from sqlalchemy.orm import Session

from app.models import Ticket
from app.schemas import TicketUpdate


def get_ticket(db: Session, ticket_id: int) -> Ticket | None:
    """Busca um ticket pelo ID."""
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def get_tickets(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    category: str | None = None,
    search: str | None = None,
) -> tuple[list[Ticket], int]:
    """
    Lista tickets com paginação e filtros opcionais.

    Returns:
        Tupla (tickets, total).
    """
    query = db.query(Ticket)

    if status:
        query = query.filter(Ticket.status == status.lower())

    if category:
        query = query.filter(Ticket.category == category.capitalize())

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Ticket.title.ilike(search_term)) | (Ticket.description.ilike(search_term))
        )

    total = query.count()
    tickets = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()

    return tickets, total


def update_ticket(db: Session, ticket: Ticket, data: TicketUpdate) -> Ticket:
    """Atualiza um ticket com os campos informados no payload."""
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(ticket, field, value)

    db.commit()
    db.refresh(ticket)
    return ticket