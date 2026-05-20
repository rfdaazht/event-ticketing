from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from domain.ticket.aggregate import Ticket
from domain.ticket.value_objects import TicketStatus
from domain.repositories.ticket_repository import ITicketRepository
from infrastructure.database.models import TicketModel


class PostgreSQLTicketRepository(ITicketRepository):
    """Concrete implementation of ITicketRepository using PostgreSQL."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, ticket: Ticket) -> None:
        existing = self._db.query(TicketModel).filter_by(id=ticket.id).first()
        if existing:
            self._update_model(existing, ticket)
        else:
            self._db.add(self._to_model(ticket))
        self._db.commit()

    def find_by_id(self, ticket_id: UUID) -> Ticket | None:
        model = self._db.query(TicketModel).filter_by(id=ticket_id).first()
        return self._to_domain(model) if model else None

    def find_by_code(self, ticket_code: str) -> Ticket | None:
        model = self._db.query(TicketModel).filter_by(ticket_code=ticket_code).first()
        return self._to_domain(model) if model else None

    def find_by_booking(self, booking_id: UUID) -> list[Ticket]:
        models = self._db.query(TicketModel).filter_by(booking_id=booking_id).all()
        return [self._to_domain(m) for m in models]

    def find_by_customer(self, customer_id: UUID) -> list[Ticket]:
        models = self._db.query(TicketModel).filter_by(customer_id=customer_id).all()
        return [self._to_domain(m) for m in models]

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _to_model(self, ticket: Ticket) -> TicketModel:
        return TicketModel(
            id=ticket.id,
            booking_id=ticket.booking_id,
            customer_id=ticket.customer_id,
            event_id=ticket.event_id,
            ticket_category_id=ticket.ticket_category_id,
            ticket_code=ticket.ticket_code,
            status=ticket.status.value,
            issued_at=ticket.issued_at,
            checked_in_at=ticket.checked_in_at,
            checked_in_by=ticket.checked_in_by,
        )

    def _update_model(self, model: TicketModel, ticket: Ticket) -> None:
        model.status = ticket.status.value
        model.checked_in_at = ticket.checked_in_at
        model.checked_in_by = ticket.checked_in_by

    def _to_domain(self, model: TicketModel) -> Ticket:
        return Ticket(
            id=model.id,
            booking_id=model.booking_id,
            customer_id=model.customer_id,
            event_id=model.event_id,
            ticket_category_id=model.ticket_category_id,
            ticket_code=model.ticket_code,
            status=TicketStatus(model.status),
            issued_at=model.issued_at,
            checked_in_at=model.checked_in_at,
            checked_in_by=model.checked_in_by,
        )