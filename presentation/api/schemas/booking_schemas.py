"""
Presentation Layer — Booking API Schemas
Pydantic models untuk request body dan response Booking endpoints.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────
# Request Schemas
# ─────────────────────────────────────────────────────────

class CreateBookingRequest(BaseModel):
    customer_id: UUID
    ticket_category_id: UUID
    quantity: int = Field(..., gt=0)


class PayBookingRequest(BaseModel):
    customer_id: UUID
    amount_paid: Decimal = Field(..., gt=0)
    currency: str = Field(default="IDR", max_length=3)


# ─────────────────────────────────────────────────────────
# Response Schemas
# ─────────────────────────────────────────────────────────

class BookingResponse(BaseModel):
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

    model_config = {"from_attributes": True}


class CreateBookingResponse(BaseModel):
    booking_id: UUID
    total_price_amount: float
    total_price_currency: str
    payment_deadline: str
    status: str


class PayBookingResponse(BaseModel):
    booking_id: UUID
    status: str
    tickets_issued: int


class ExpireBookingResponse(BaseModel):
    booking_id: UUID
    status: str
