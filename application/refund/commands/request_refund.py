from dataclasses import dataclass
from uuid import UUID

from domain.event.value_objects import EventStatus
from domain.refund.aggregate import Refund
from domain.repositories.booking_repository import IBookingRepository
from domain.repositories.event_repository import IEventRepository
from domain.repositories.ticket_repository import ITicketRepository
from domain.repositories.refund_repository import IRefundRepository


@dataclass
class RequestRefundCommand:
    """Command data for requesting a refund."""
    booking_id: UUID
    customer_id: UUID
    reason: str = ""


@dataclass
class RequestRefundResult:
    """Result returned after successfully requesting a refund."""
    refund_id: UUID
    booking_id: UUID
    status: str


class RequestRefundHandler:
    """Handles the RequestRefund command."""

    def __init__(
        self,
        booking_repository: IBookingRepository,
        event_repository: IEventRepository,
        ticket_repository: ITicketRepository,
        refund_repository: IRefundRepository,
    ) -> None:
        self._booking_repository = booking_repository
        self._event_repository = event_repository
        self._ticket_repository = ticket_repository
        self._refund_repository = refund_repository

    def handle(self, command: RequestRefundCommand) -> RequestRefundResult:
        # Load and validate booking
        booking = self._booking_repository.find_by_id(command.booking_id)
        if booking is None:
            raise ValueError(f"Booking {command.booking_id} not found.")
        if booking.customer_id != command.customer_id:
            raise ValueError("This booking does not belong to this customer.")
        if booking.status.value != "paid":
            raise ValueError("Refund can only be requested for a paid booking.")

        # if the event has been cancelled, a refund is automatically allowed regardless of the refund deadline.
        event = self._event_repository.find_by_id(booking.event_id)
        event_is_cancelled = event is not None and event.status == EventStatus.CANCELLED
        if not event_is_cancelled and booking.is_refund_deadline_passed:
            raise ValueError("Refund deadline has passed.")

        # Rule: cannot request refund if any ticket is already checked in
        tickets = self._ticket_repository.find_by_booking(command.booking_id)
        checked_in = [t for t in tickets if t.is_checked_in]
        if checked_in:
            raise ValueError(
                "Refund cannot be requested because a ticket has already been checked in."
            )

        # Create refund aggregate
        refund = Refund.request(
            booking_id=command.booking_id,
            customer_id=command.customer_id,
            amount=booking.total_price,
            reason=command.reason,
        )
        self._refund_repository.save(refund)
        refund.pull_domain_events()

        return RequestRefundResult(
            refund_id=refund.id,
            booking_id=refund.booking_id,
            status=refund.status.value,
        )