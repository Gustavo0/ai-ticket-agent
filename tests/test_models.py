"""
Testes do modelo ORM Ticket.
"""

from app.db.session import Base, engine, SessionLocal
from app.models import Ticket


class TestTicketModel:
    """Testes do modelo ORM Ticket."""

    def setup_method(self):
        """Recria as tabelas antes de cada teste."""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def test_create_ticket(self):
        """Deve criar um ticket com os campos básicos."""
        session = SessionLocal()
        try:
            ticket = Ticket(
                title="Chamado de teste",
                description="Descrição do chamado de teste.",
                category="Suporte",
                priority="Alta",
                status="aberto",
            )
            session.add(ticket)
            session.commit()
            session.refresh(ticket)

            assert ticket.id is not None
            assert ticket.title == "Chamado de teste"
            assert ticket.description == "Descrição do chamado de teste."
            assert ticket.category == "Suporte"
            assert ticket.priority == "Alta"
            assert ticket.status == "aberto"
        finally:
            session.close()

    def test_ticket_default_status(self):
        """O status padrão de um ticket deve ser 'aberto'."""
        session = SessionLocal()
        try:
            ticket = Ticket(
                title="Chamado sem status",
                description="Descrição do chamado.",
            )
            session.add(ticket)
            session.commit()
            session.refresh(ticket)

            assert ticket.status == "aberto"
        finally:
            session.close()

    def test_ticket_has_timestamps(self):
        """O ticket deve ter created_at e updated_at preenchidos."""
        session = SessionLocal()
        try:
            ticket = Ticket(
                title="Chamado com timestamps",
                description="Descrição do chamado.",
            )
            session.add(ticket)
            session.commit()
            session.refresh(ticket)

            assert ticket.created_at is not None
            assert ticket.updated_at is not None
        finally:
            session.close()

    def test_ticket_repr(self):
        """O __repr__ do ticket deve ser informativo."""
        session = SessionLocal()
        try:
            ticket = Ticket(
                title="Chamado para repr",
                description="Descrição do chamado.",
            )
            session.add(ticket)
            session.commit()
            session.refresh(ticket)

            expected = f"<Ticket id={ticket.id} title='Chamado para repr' status='aberto'>"
            assert repr(ticket) == expected
        finally:
            session.close()

    def test_ticket_query_by_id(self):
        """Deve ser possível buscar um ticket pelo ID."""
        session = SessionLocal()
        try:
            ticket = Ticket(
                title="Chamado para busca",
                description="Descrição do chamado.",
            )
            session.add(ticket)
            session.commit()
            session.refresh(ticket)

            found = session.query(Ticket).filter(Ticket.id == ticket.id).first()
            assert found is not None
            assert found.title == "Chamado para busca"
        finally:
            session.close()

    def test_ticket_query_all(self):
        """Deve ser possível listar todos os tickets."""
        session = SessionLocal()
        try:
            ticket1 = Ticket(title="Ticket 1", description="Descrição 1.")
            ticket2 = Ticket(title="Ticket 2", description="Descrição 2.")
            session.add_all([ticket1, ticket2])
            session.commit()

            tickets = session.query(Ticket).all()
            assert len(tickets) == 2
        finally:
            session.close()

    def test_ticket_update(self):
        """Deve ser possível atualizar um ticket."""
        session = SessionLocal()
        try:
            ticket = Ticket(
                title="Chamado original",
                description="Descrição original.",
                status="aberto",
            )
            session.add(ticket)
            session.commit()

            ticket.status = "em andamento"
            session.commit()
            session.refresh(ticket)

            assert ticket.status == "em andamento"
        finally:
            session.close()