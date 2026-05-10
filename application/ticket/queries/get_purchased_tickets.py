from dataclasses import dataclass
from uuid import UUID

from domain.repositories.ticket_repository import ITicketRepository


@dataclass
class GetPurchasedTicketsQuery:
    """Query data for fetching all tickets owned by a customer."""
    customer_id: UUID


@dataclass
class PurchasedTicketDetail:
    """Detail data for a single purchased ticket."""
    ticket_id: UUID
    ticket_code: str
    event_id: UUID
    ticket_category_id: UUID
    status: str
    issued_at: str
    checked_in_at: str | None


class GetPurchasedTicketsHandler:
    """
    Handles the GetPurchasedTickets query.
    Returns all active tickets owned by the customer.
    """

    def __init__(self, ticket_repository: ITicketRepository) -> None:
        self._ticket_repository = ticket_repository

    def handle(self, query: GetPurchasedTicketsQuery) -> list[PurchasedTicketDetail]:
        tickets = self._ticket_repository.find_by_customer(query.customer_id)

        return [
            PurchasedTicketDetail(
                ticket_id=ticket.id,
                ticket_code=ticket.ticket_code,
                event_id=ticket.event_id,
                ticket_category_id=ticket.ticket_category_id,
                status=ticket.status.value,
                issued_at=ticket.issued_at.isoformat(),
                checked_in_at=(
                    ticket.checked_in_at.isoformat()
                    if ticket.checked_in_at else None
                ),
            )
            for ticket in tickets
        ]