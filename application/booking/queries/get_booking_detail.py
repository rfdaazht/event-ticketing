from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from domain.repositories.booking_repository import IBookingRepository


@dataclass
class GetBookingDetailQuery:
    """Query data for fetching a single booking's details."""
    booking_id: UUID
    customer_id: UUID


@dataclass
class BookingDetail:
    """Full detail data for a single booking."""
    booking_id: UUID
    customer_id: UUID
    event_id: UUID
    ticket_category_id: UUID
    quantity: int
    total_price_amount: Decimal
    total_price_currency: str
    status: str
    payment_deadline: datetime
    created_at: datetime


class GetBookingDetailHandler:
    """
    Handles the GetBookingDetail query.
    Customers can only view their own bookings.
    """

    def __init__(self, booking_repository: IBookingRepository) -> None:
        self._booking_repository = booking_repository

    def handle(self, query: GetBookingDetailQuery) -> BookingDetail:
        booking = self._booking_repository.find_by_id(query.booking_id)
        if booking is None:
            raise ValueError(f"Booking {query.booking_id} not found.")
        if booking.customer_id != query.customer_id:
            raise ValueError("This booking does not belong to this customer.")

        return BookingDetail(
            booking_id=booking.id,
            customer_id=booking.customer_id,
            event_id=booking.event_id,
            ticket_category_id=booking.ticket_category_id,
            quantity=booking.quantity,
            total_price_amount=booking.total_price.amount,
            total_price_currency=booking.total_price.currency,
            status=booking.status.value,
            payment_deadline=booking.payment_deadline,
            created_at=booking.created_at,
        )