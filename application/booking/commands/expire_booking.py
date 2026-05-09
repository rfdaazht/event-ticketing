from dataclasses import dataclass
from uuid import UUID

from domain.repositories.booking_repository import IBookingRepository
from domain.repositories.event_repository import IEventRepository


@dataclass
class ExpireBookingCommand:
    """Command data for expiring a single booking."""
    booking_id: UUID


@dataclass
class ExpireBookingResult:
    """Result returned after successfully expiring a booking."""
    booking_id: UUID
    status: str


class ExpireBookingHandler:
    """
    Handles the ExpireBooking command.
    Called by the system automatically after payment deadline passes.
    """

    def __init__(
        self,
        booking_repository: IBookingRepository,
        event_repository: IEventRepository,
    ) -> None:
        self._booking_repository = booking_repository
        self._event_repository = event_repository

    def handle(self, command: ExpireBookingCommand) -> ExpireBookingResult:
        booking = self._booking_repository.find_by_id(command.booking_id)
        if booking is None:
            raise ValueError(f"Booking {command.booking_id} not found.")

        # Release reserved quota back to ticket category
        event = self._event_repository.find_by_id(booking.event_id)
        if event is not None:
            for tc in event.ticket_categories:
                if tc.id == booking.ticket_category_id:
                    tc.release(booking.quantity)
                    self._event_repository.save(event)
                    break

        # Mark booking as expired
        booking.expire()
        self._booking_repository.save(booking)
        booking.pull_domain_events()

        return ExpireBookingResult(
            booking_id=booking.id,
            status=booking.status.value,
        )