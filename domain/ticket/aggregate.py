from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from uuid import UUID, uuid4

from domain.shared.base import AggregateRoot
from domain.shared.events import TicketCheckedIn
from domain.ticket.value_objects import TicketStatus

CHECK_IN_WINDOW = timedelta(hours=0)


def _generate_ticket_code() -> str:
    """Generate a unique readable ticket code. Example: TKT-A1B2C3D4"""
    import random
    import string
    chars = string.ascii_uppercase + string.digits
    suffix = "".join(random.choices(chars, k=8))
    return f"TKT-{suffix}"


class TicketAlreadyCheckedInError(ValueError):
    """Raised when a ticket that was already checked in is scanned again."""


class TicketCancelledError(ValueError):
    """Raised when a cancelled ticket is scanned."""


class TicketEventMismatchError(ValueError):
    """Raised when a ticket is scanned at the wrong event's gate."""


class TicketOutsideCheckInWindowError(ValueError):
    """Raised when check-in is attempted outside the event's allowed time window."""


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

    def check_in(
        self,
        gate_officer_id: UUID,
        event_id: UUID,
        event_start_date: date,
        event_end_date: date,
        now: datetime = None,
    ) -> None:
        """
        Validate and check in this ticket at the event gate.
        Enforces all check-in business rules, including US13's
        requirement that check-in can only happen on the event day
        or within the allowed check-in time window.

        event_start_date / event_end_date come from the Event aggregate;
        the caller (application layer) is responsible for loading them,
        since Ticket does not hold a reference to Event's full state.
        """
        if self.event_id != event_id:
            raise TicketEventMismatchError(
                "This ticket does not match the event."
            )
        if self.status == TicketStatus.CHECKED_IN:
            raise TicketAlreadyCheckedInError(
                "This ticket has already been used."
            )
        if self.status == TicketStatus.CANCELLED:
            raise TicketCancelledError(
                "This ticket has been cancelled."
            )
        if self.status != TicketStatus.ACTIVE:
            raise ValueError("Only an active ticket can be checked in.")

        now = now or datetime.utcnow()
        window_start = datetime.combine(event_start_date, datetime.min.time()) - CHECK_IN_WINDOW
        window_end = datetime.combine(event_end_date, datetime.max.time()) + CHECK_IN_WINDOW
        if not (window_start <= now <= window_end):
            raise TicketOutsideCheckInWindowError(
                "Check-in is only allowed on the event day or within the "
                "allowed check-in time window."
            )

        self.status = TicketStatus.CHECKED_IN
        self.checked_in_at = now
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