"""
Presentation Layer — Event API Schemas
Pydantic models untuk request body dan response Event & TicketCategory endpoints.
"""

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────
# Request Schemas
# ─────────────────────────────────────────────────────────

class CreateEventRequest(BaseModel):
    organizer_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(default="")
    location: str = Field(..., min_length=1, max_length=255)
    start_date: date
    end_date: date
    max_capacity: int = Field(..., gt=0)


class PublishEventRequest(BaseModel):
    organizer_id: UUID


class CancelEventRequest(BaseModel):
    organizer_id: UUID


class CreateTicketCategoryRequest(BaseModel):
    organizer_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    price_amount: Decimal = Field(..., gt=0)
    price_currency: str = Field(default="IDR", max_length=3)
    quota: int = Field(..., gt=0)
    sales_start: date
    sales_end: date


class DisableTicketCategoryRequest(BaseModel):
    organizer_id: UUID


# ─────────────────────────────────────────────────────────
# Response Schemas
# ─────────────────────────────────────────────────────────

class TicketCategoryResponse(BaseModel):
    category_id: UUID
    name: str
    price_amount: Decimal
    price_currency: str
    quota: int
    remaining_quota: int
    sales_start: date
    sales_end: date
    availability_status: str

    model_config = {"from_attributes": True}


class EventResponse(BaseModel):
    event_id: UUID
    name: str
    description: str
    location: str
    start_date: date
    end_date: date
    max_capacity: int
    status: str
    organizer_id: UUID

    model_config = {"from_attributes": True}


class EventDetailResponse(BaseModel):
    event_id: UUID
    name: str
    description: str
    location: str
    start_date: date
    end_date: date
    organizer_id: UUID
    status: str
    ticket_categories: list[TicketCategoryResponse]

    model_config = {"from_attributes": True}


class EventListItemResponse(BaseModel):
    event_id: UUID
    name: str
    location: str
    start_date: date
    end_date: date
    lowest_price: Decimal
    currency: str

    model_config = {"from_attributes": True}


class CreateEventResponse(BaseModel):
    event_id: UUID
    name: str
    status: str


class PublishEventResponse(BaseModel):
    event_id: UUID
    status: str


class CancelEventResponse(BaseModel):
    event_id: UUID
    status: str


class CreateTicketCategoryResponse(BaseModel):
    category_id: UUID
    name: str
    quota: int


class DisableTicketCategoryResponse(BaseModel):
    category_id: UUID
    status: str


# ─────────────────────────────────────────────────────────
# Report / Participant Schemas
# ─────────────────────────────────────────────────────────

class ParticipantResponse(BaseModel):
    customer_id: UUID
    ticket_code: str
    ticket_category_name: str
    check_in_status: str


class CategorySalesResponse(BaseModel):
    category_id: UUID
    name: str
    quota: int
    sold: int
    remaining: int


class SalesReportResponse(BaseModel):
    event_id: UUID
    event_name: str
    total_revenue: Decimal
    currency: str
    booking_count_pending: int
    booking_count_paid: int
    booking_count_expired: int
    booking_count_refunded: int
    categories: list[CategorySalesResponse]
