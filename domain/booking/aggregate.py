from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID

from domain.shared.base import AggregateRoot
from domain.shared.value_objects import Money
from domain.shared.events import (
    TicketReserved,
    BookingPaid,
    BookingExpired,
)
from domain.booking.value_objects import BookingStatus

PAYMENT_DEADLINE_MINUTES = 15


@dataclass(eq=False)
class Booking(AggregateRoot):
    """
    Aggregate root for the Booking domain.
    Represents a reservation made by a customer before payment.
    """
    customer_id: UUID = field(default=None)
    event_id: UUID = field(default=None)
    ticket_category_id: UUID = field(default=None)
    quantity: int = field(default=0)
    unit_price: Money = field(default=None)
    total_price: Money = field(default=None)
    status: BookingStatus = field(default=BookingStatus.PENDING_PAYMENT)
    payment_deadline: datetime = field(default=None)
    created_at: datetime = field(default_factory=datetime.utcnow)

    # ─ Factory Method

    @classmethod
    def create(
        cls,
        customer_id: UUID,
        event_id: UUID,
        ticket_category_id: UUID,
        quantity: int,
        unit_price: Money,
    ) -> "Booking":
        """
        The only valid way to create a new Booking.
        Enforces all business rules on creation.
        """
        if quantity <= 0:
            raise ValueError("Ticket quantity must be greater than zero.")

        total_price = unit_price.multiply(quantity)
        created_at = datetime.utcnow()
        payment_deadline = created_at + timedelta(minutes=PAYMENT_DEADLINE_MINUTES)

        booking = cls(
            customer_id=customer_id,
            event_id=event_id,
            ticket_category_id=ticket_category_id,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
            status=BookingStatus.PENDING_PAYMENT,
            payment_deadline=payment_deadline,
            created_at=created_at,
        )

        booking._record_event(
            TicketReserved(
                booking_id=booking.id,
                customer_id=customer_id,
                event_id=event_id,
            )
        )
        return booking

    # ─ Properties

    @property
    def is_payment_deadline_passed(self) -> bool:
        return datetime.utcnow() > self.payment_deadline

    # ─ Business Methods

    def pay(self, amount_paid: Money) -> None:
        """Confirm payment for this booking."""
        if self.status != BookingStatus.PENDING_PAYMENT:
            raise ValueError("Only a pending payment booking can be paid.")
        if self.is_payment_deadline_passed:
            raise ValueError("Payment deadline has passed.")
        if not amount_paid.is_equal_to(self.total_price):
            raise ValueError(
                f"Payment amount {amount_paid} does not match "
                f"total price {self.total_price}."
            )

        self.status = BookingStatus.PAID
        self._record_event(
            BookingPaid(
                booking_id=self.id,
                customer_id=self.customer_id,
            )
        )

    def expire(self) -> None:
        """Mark this booking as expired after payment deadline passes."""
        if self.status == BookingStatus.PAID:
            raise ValueError("A paid booking cannot be expired.")
        if self.status != BookingStatus.PENDING_PAYMENT:
            raise ValueError("Only a pending payment booking can be expired.")

        self.status = BookingStatus.EXPIRED
        self._record_event(
            BookingExpired(
                booking_id=self.id,
                event_id=self.event_id,
            )
        )

    def mark_as_refunded(self) -> None:
        """Mark this booking as refunded after refund is approved."""
        if self.status != BookingStatus.PAID:
            raise ValueError("Only a paid booking can be marked as refunded.")
        self.status = BookingStatus.REFUNDED