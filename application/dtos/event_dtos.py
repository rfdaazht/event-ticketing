from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID


# ─ Request DTOs

@dataclass
class CreateEventRequest:
    organizer_id: UUID
    name: str
    description: str
    location: str
    start_date: date
    end_date: date
    max_capacity: int


@dataclass
class CreateTicketCategoryRequest:
    organizer_id: UUID
    name: str
    price_amount: Decimal
    price_currency: str
    quota: int
    sales_start: date
    sales_end: date


@dataclass
class PublishEventRequest:
    organizer_id: UUID


@dataclass
class CancelEventRequest:
    organizer_id: UUID


@dataclass
class DisableTicketCategoryRequest:
    organizer_id: UUID


# - Response DTOs

@dataclass
class EventResponse:
    event_id: UUID
    name: str
    description: str
    location: str
    start_date: date
    end_date: date
    max_capacity: int
    status: str
    organizer_id: UUID


@dataclass
class TicketCategoryResponse:
    category_id: UUID
    name: str
    price_amount: Decimal
    price_currency: str
    quota: int
    remaining_quota: int
    sales_start: date
    sales_end: date
    status: str
    availability_status: str


@dataclass
class EventListItemResponse:
    event_id: UUID
    name: str
    location: str
    start_date: date
    end_date: date
    lowest_price: Decimal
    currency: str