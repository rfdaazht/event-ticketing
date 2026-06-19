from dataclasses import dataclass
from uuid import UUID

from domain.event.value_objects import EventStatus
from domain.repositories.event_repository import IEventRepository
from domain.repositories.ticket_repository import ITicketRepository
from domain.ticket.aggregate import (
    TicketAlreadyCheckedInError,
    TicketCancelledError,
    TicketEventMismatchError,
    TicketOutsideCheckInWindowError,
)


class TicketNotFoundError(ValueError):
    """Raised when the scanned ticket code does not exist."""


class EventCancelledError(ValueError):
    """Raised when check-in is attempted for a cancelled event."""


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

    Maps each US14 failure scenario to a distinct exception so the
    presentation layer can return the exact message required:
    - ticket not found -> TicketNotFoundError
    - event cancelled -> EventCancelledError
    - already checked in -> TicketAlreadyCheckedInError
    - wrong event -> TicketEventMismatchError
    - outside check-in window -> TicketOutsideCheckInWindowError
    """

    def __init__(
        self,
        ticket_repository: ITicketRepository,
        event_repository: IEventRepository,
    ) -> None:
        self._ticket_repository = ticket_repository
        self._event_repository = event_repository

    def handle(self, command: CheckInTicketCommand) -> CheckInTicketResult:
        # US14: ticket code not found
        ticket = self._ticket_repository.find_by_code(command.ticket_code)
        if ticket is None:
            raise TicketNotFoundError(
                f"Ticket with code '{command.ticket_code}' is invalid."
            )

        # Load the event to get its dates and current status.
        event = self._event_repository.find_by_id(command.event_id)
        if event is None:
            raise ValueError(f"Event {command.event_id} not found.")

        # US14: event has been cancelled
        if event.status == EventStatus.CANCELLED:
            raise EventCancelledError("This event has been cancelled.")

        # Remaining business rules enforced inside ticket.check_in(): already checked in, cancelled ticket, wrong event, outside window.
        ticket.check_in(
            gate_officer_id=command.gate_officer_id,
            event_id=command.event_id,
            event_start_date=event.start_date,
            event_end_date=event.end_date,
        )

        self._ticket_repository.save(ticket)
        ticket.pull_domain_events()

        return CheckInTicketResult(
            ticket_id=ticket.id,
            ticket_code=ticket.ticket_code,
            status=ticket.status.value,
            checked_in_at=ticket.checked_in_at.isoformat(),
        )