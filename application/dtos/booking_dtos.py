from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


# ─ Request DTOs

@dataclass
class CreateBookingRequest:
    customer_id: UUID
    ticket_category_id: UUID
    quantity: int


@dataclass
class PayBookingRequest:
    customer_id: UUID
    amount_paid: Decimal
    currency: str


# ─ Response DTOs

@dataclass
class BookingResponse:
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


@dataclass
class PayBookingResponse:
    booking_id: UUID
    status: str
    tickets_issued: int