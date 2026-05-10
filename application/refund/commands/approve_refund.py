from dataclasses import dataclass
from uuid import UUID

from domain.repositories.refund_repository import IRefundRepository
from domain.repositories.booking_repository import IBookingRepository
from domain.repositories.ticket_repository import ITicketRepository


@dataclass
class ApproveRefundCommand:
    """Command data for approving a refund request."""
    refund_id: UUID
    organizer_id: UUID


@dataclass
class ApproveRefundResult:
    """Result returned after successfully approving a refund."""
    refund_id: UUID
    status: str


class ApproveRefundHandler:
    """Handles the ApproveRefund command."""

    def __init__(
        self,
        refund_repository: IRefundRepository,
        booking_repository: IBookingRepository,
        ticket_repository: ITicketRepository,
    ) -> None:
        self._refund_repository = refund_repository
        self._booking_repository = booking_repository
        self._ticket_repository = ticket_repository

    def handle(self, command: ApproveRefundCommand) -> ApproveRefundResult:
        refund = self._refund_repository.find_by_id(command.refund_id)
        if refund is None:
            raise ValueError(f"Refund {command.refund_id} not found.")

        # Approve refund — business rules enforced inside approve()
        refund.approve()
        self._refund_repository.save(refund)

        # Cancel all related tickets
        tickets = self._ticket_repository.find_by_booking(refund.booking_id)
        for ticket in tickets:
            ticket.cancel()
            self._ticket_repository.save(ticket)

        # Mark booking as refunded
        booking = self._booking_repository.find_by_id(refund.booking_id)
        if booking is not None:
            booking.mark_as_refunded()
            self._booking_repository.save(booking)

        refund.pull_domain_events()

        return ApproveRefundResult(
            refund_id=refund.id,
            status=refund.status.value,
        )