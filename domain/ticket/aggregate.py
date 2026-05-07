from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from domain.shared.base import AggregateRoot
from domain.shared.events import TicketCheckedIn
from domain.ticket.value_objects import TicketStatus


def _generate_ticket_code() -> str:
    """Generate a unique readable ticket code. Example: TKT-A1B2C3D4"""
    import random
    import string
    chars = string.ascii_uppercase + string.digits
    suffix = "".join(random.choices(chars, k=8))
    return f"TKT-{suffix}"


@dataclass(eq=False)
class Ticket(AggregateRoot):
    """
    Aggregate root for the Ticket domain.
    Represents proof of attendance issued after a Booking is paid.
    Has its own lifecycle independent from Booking.
    """
    booking_id: UUID = field(default=None)
    customer_id: UUID = field(default=None)
    event_id: UUID = field(default=None)
    ticket_category_id: UUID = field(default=None)
    ticket_code: str = field(default_factory=_generate_ticket_code)
    status: TicketStatus = field(default=TicketStatus.ACTIVE)
    issued_at: datetime = field(default_factory=datetime.utcnow)
    checked_in_at: datetime = field(default=None)
    checked_in_by: UUID = field(default=None)

    # ─ Factory Method

    @classmethod
    def issue(
        cls,
        booking_id: UUID,
        customer_id: UUID,
        event_id: UUID,
        ticket_category_id: UUID,
    ) -> "Ticket":
        """
        The only valid way to issue a new Ticket.
        Called after a Booking is successfully paid.
        """
        ticket = cls(
            booking_id=booking_id,
            customer_id=customer_id,
            event_id=event_id,
            ticket_category_id=ticket_category_id,
        )
        return ticket

    # ─ Business Methods

    def check_in(self, gate_officer_id: UUID, event_id: UUID) -> None:
        """
        Validate and check in this ticket at the event gate.
        Enforces all check-in business rules.
        """
        if self.event_id != event_id:
            raise ValueError("This ticket does not belong to this event.")
        if self.status == TicketStatus.CHECKED_IN:
            raise ValueError("This ticket has already been checked in.")
        if self.status == TicketStatus.CANCELLED:
            raise ValueError("This ticket has been cancelled.")
        if self.status != TicketStatus.ACTIVE:
            raise ValueError("Only an active ticket can be checked in.")

        self.status = TicketStatus.CHECKED_IN
        self.checked_in_at = datetime.utcnow()
        self.checked_in_by = gate_officer_id

        self._record_event(
            TicketCheckedIn(
                ticket_id=self.id,
                event_id=self.event_id,
                checked_in_by=gate_officer_id,
            )
        )

    def cancel(self) -> None:
        """Cancel this ticket, e.g. when a refund is approved."""
        if self.status == TicketStatus.CHECKED_IN:
            raise ValueError("A checked-in ticket cannot be cancelled.")
        if self.status == TicketStatus.CANCELLED:
            raise ValueError("This ticket is already cancelled.")

        self.status = TicketStatus.CANCELLED

    # ─ Properties

    @property
    def is_active(self) -> bool:
        return self.status == TicketStatus.ACTIVE

    @property
    def is_checked_in(self) -> bool:
        return self.status == TicketStatus.CHECKED_IN