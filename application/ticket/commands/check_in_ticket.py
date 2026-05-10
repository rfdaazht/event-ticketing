from dataclasses import dataclass
from uuid import UUID

from domain.repositories.ticket_repository import ITicketRepository


@dataclass
class CheckInTicketCommand:
    """Command data for checking in a ticket at the event gate."""
    ticket_code: str
    event_id: UUID
    gate_officer_id: UUID


@dataclass
class CheckInTicketResult:
    """Result returned after successfully checking in a ticket."""
    ticket_id: UUID
    ticket_code: str
    status: str
    checked_in_at: str


class CheckInTicketHandler:
    """
    Handles the CheckInTicket command.
    Called by the Gate Officer when scanning a ticket at the gate.
    """

    def __init__(self, ticket_repository: ITicketRepository) -> None:
        self._ticket_repository = ticket_repository

    def handle(self, command: CheckInTicketCommand) -> CheckInTicketResult:
        # Find ticket by code
        ticket = self._ticket_repository.find_by_code(command.ticket_code)
        if ticket is None:
            raise ValueError(
                f"Ticket with code '{command.ticket_code}' is invalid or not found."
            )

        # Business rules enforced inside ticket.check_in()
        ticket.check_in(
            gate_officer_id=command.gate_officer_id,
            event_id=command.event_id,
        )

        self._ticket_repository.save(ticket)
        ticket.pull_domain_events()

        return CheckInTicketResult(
            ticket_id=ticket.id,
            ticket_code=ticket.ticket_code,
            status=ticket.status.value,
            checked_in_at=ticket.checked_in_at.isoformat(),
        )