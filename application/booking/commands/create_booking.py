from dataclasses import dataclass
from datetime import date
from uuid import UUID

from domain.booking.aggregate import Booking
from domain.event.value_objects import EventStatus
from domain.repositories.event_repository import IEventRepository
from domain.repositories.booking_repository import IBookingRepository


@dataclass
class CreateBookingCommand:
    """Command data for creating a new booking."""
    customer_id: UUID
    event_id: UUID
    ticket_category_id: UUID
    quantity: int


@dataclass
class CreateBookingResult:
    """Result returned after successfully creating a booking."""
    booking_id: UUID
    total_price_amount: float
    total_price_currency: str
    payment_deadline: str
    status: str


class CreateBookingHandler:
    """Handles the CreateBooking command."""

    def __init__(
        self,
        event_repository: IEventRepository,
        booking_repository: IBookingRepository,
    ) -> None:
        self._event_repository = event_repository
        self._booking_repository = booking_repository

    def handle(self, command: CreateBookingCommand) -> CreateBookingResult:
        # Load and validate event
        event = self._event_repository.find_by_id(command.event_id)
        if event is None:
            raise ValueError(f"Event {command.event_id} not found.")
        if event.status != EventStatus.PUBLISHED:
            raise ValueError("Booking can only be created for a published event.")

        # Find the ticket category
        category = None
        for tc in event.ticket_categories:
            if tc.id == command.ticket_category_id:
                category = tc
                break
        if category is None:
            raise ValueError("Ticket category not found.")
        if not category.is_active:
            raise ValueError("Ticket category is not active.")
        if not category.is_within_sales_period(date.today()):
            raise ValueError("Ticket category is outside its sales period.")
        if command.quantity > category.remaining_quota:
            raise ValueError(
                f"Not enough quota. Requested: {command.quantity}, "
                f"Available: {category.remaining_quota}."
            )

        # Enforce one active booking per customer per event
        existing = self._booking_repository.find_by_customer_and_event(
            command.customer_id, command.event_id
        )
        if existing is not None:
            raise ValueError(
                "Customer already has an active booking for this event."
            )

        # Reserve quota on the category
        category.reserve(command.quantity)
        self._event_repository.save(event)

        # Create booking aggregate
        booking = Booking.create(
            customer_id=command.customer_id,
            event_id=command.event_id,
            ticket_category_id=command.ticket_category_id,
            quantity=command.quantity,
            unit_price=category.price,
        )
        self._booking_repository.save(booking)
        booking.pull_domain_events()

        return CreateBookingResult(
            booking_id=booking.id,
            total_price_amount=float(booking.total_price.amount),
            total_price_currency=booking.total_price.currency,
            payment_deadline=booking.payment_deadline.isoformat(),
            status=booking.status.value,
        )