from dataclasses import dataclass
from uuid import UUID

from domain.repositories.event_repository import IEventRepository
from domain.repositories.booking_repository import IBookingRepository
from domain.repositories.ticket_repository import ITicketRepository


@dataclass
class GetParticipantsQuery:
    """Query data for fetching participant list for an event."""
    event_id: UUID
    organizer_id: UUID


@dataclass
class ParticipantDetail:
    """Detail data for a single participant."""
    customer_id: UUID
    ticket_code: str
    ticket_category_name: str
    check_in_status: str  # "checked_in" or "not_checked_in"


class GetParticipantsHandler:
    """Handles the GetParticipants query."""

    def __init__(
        self,
        event_repository: IEventRepository,
        booking_repository: IBookingRepository,
        ticket_repository: ITicketRepository,
    ) -> None:
        self._event_repository = event_repository
        self._booking_repository = booking_repository
        self._ticket_repository = ticket_repository

    def handle(self, query: GetParticipantsQuery) -> list[ParticipantDetail]:
        event = self._event_repository.find_by_id(query.event_id)
        if event is None:
            raise ValueError(f"Event {query.event_id} not found.")
        if event.organizer_id != query.organizer_id:
            raise ValueError("Only the event organizer can view participants.")

        # Only paid bookings count as participants
        bookings = self._booking_repository.find_by_event(query.event_id)
        paid_bookings = [b for b in bookings if b.status.value == "paid"]

        # Build category name lookup
        category_map = {tc.id: tc.name for tc in event.ticket_categories}

        participants = []
        for booking in paid_bookings:
            tickets = self._ticket_repository.find_by_booking(booking.id)
            for ticket in tickets:
                participants.append(ParticipantDetail(
                    customer_id=booking.customer_id,
                    ticket_code=ticket.ticket_code,
                    ticket_category_name=category_map.get(
                        ticket.ticket_category_id, "Unknown"
                    ),
                    check_in_status=(
                        "checked_in"
                        if ticket.is_checked_in
                        else "not_checked_in"
                    ),
                ))

        return participants