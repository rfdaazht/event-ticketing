from dataclasses import dataclass, field
from uuid import UUID

from domain.shared.base import DomainEvent


# ─ Event Management

@dataclass(frozen=True)
class EventCreated(DomainEvent):
    """Raised when a new event is successfully created."""
    event_id: UUID = field(default=None)
    name: str = field(default="")
    organizer_id: UUID = field(default=None)


@dataclass(frozen=True)
class EventPublished(DomainEvent):
    """Raised when an event is published and visible to customers."""
    event_id: UUID = field(default=None)


@dataclass(frozen=True)
class EventCancelled(DomainEvent):
    """Raised when an event is cancelled by the organizer."""
    event_id: UUID = field(default=None)


# ─ Ticket Category

@dataclass(frozen=True)
class TicketCategoryCreated(DomainEvent):
    """Raised when a new ticket category is added to an event."""
    event_id: UUID = field(default=None)
    category_id: UUID = field(default=None)
    name: str = field(default="")


@dataclass(frozen=True)
class TicketCategoryDisabled(DomainEvent):
    """Raised when a ticket category is deactivated."""
    event_id: UUID = field(default=None)
    category_id: UUID = field(default=None)


# ─ Booking

@dataclass(frozen=True)
class TicketReserved(DomainEvent):
    """Raised when a booking is created and quota is reserved."""
    booking_id: UUID = field(default=None)
    customer_id: UUID = field(default=None)
    event_id: UUID = field(default=None)


@dataclass(frozen=True)
class BookingPaid(DomainEvent):
    """Raised when a booking payment is confirmed."""
    booking_id: UUID = field(default=None)
    customer_id: UUID = field(default=None)


@dataclass(frozen=True)
class BookingExpired(DomainEvent):
    """Raised when a booking expires due to unpaid payment deadline."""
    booking_id: UUID = field(default=None)
    event_id: UUID = field(default=None)


# ─ Ticket

@dataclass(frozen=True)
class TicketCheckedIn(DomainEvent):
    """Raised when a ticket is successfully validated at the gate."""
    ticket_id: UUID = field(default=None)
    event_id: UUID = field(default=None)
    checked_in_by: UUID = field(default=None)


# ─ Refund

@dataclass(frozen=True)
class RefundRequested(DomainEvent):
    """Raised when a customer submits a refund request."""
    refund_id: UUID = field(default=None)
    booking_id: UUID = field(default=None)
    customer_id: UUID = field(default=None)


@dataclass(frozen=True)
class RefundApproved(DomainEvent):
    """Raised when an organizer approves a refund request."""
    refund_id: UUID = field(default=None)
    booking_id: UUID = field(default=None)


@dataclass(frozen=True)
class RefundRejected(DomainEvent):
    """Raised when an organizer rejects a refund request."""
    refund_id: UUID = field(default=None)
    booking_id: UUID = field(default=None)
    reason: str = field(default="")


@dataclass(frozen=True)
class RefundPaidOut(DomainEvent):
    """Raised when a refund is successfully disbursed to the customer."""
    refund_id: UUID = field(default=None)
    payment_reference: str = field(default="")