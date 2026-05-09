from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from domain.repositories.event_repository import IEventRepository


@dataclass
class GetEventDetailQuery:
    """Query data for fetching a single event's details."""
    event_id: UUID


@dataclass
class TicketCategoryDetail:
    """Detail data for a single ticket category."""
    category_id: UUID
    name: str
    price_amount: Decimal
    price_currency: str
    quota: int
    remaining_quota: int
    sales_start: date
    sales_end: date
    availability_status: str  # "available", "coming_soon", "sales_closed", "sold_out"


@dataclass
class EventDetail:
    """Full detail data for a single event."""
    event_id: UUID
    name: str
    description: str
    location: str
    start_date: date
    end_date: date
    organizer_id: UUID
    status: str
    ticket_categories: list[TicketCategoryDetail]


class GetEventDetailHandler:
    """Handles the GetEventDetail query."""

    def __init__(self, event_repository: IEventRepository) -> None:
        self._event_repository = event_repository

    def handle(self, query: GetEventDetailQuery) -> EventDetail:
        event = self._event_repository.find_by_id(query.event_id)
        if event is None:
            raise ValueError(f"Event {query.event_id} not found.")

        today = date.today()
        categories = []

        for tc in event.active_categories:
            # Determine availability status
            if tc.remaining_quota == 0:
                availability = "sold_out"
            elif today < tc.sales_start:
                availability = "coming_soon"
            elif today > tc.sales_end:
                availability = "sales_closed"
            else:
                availability = "available"

            categories.append(TicketCategoryDetail(
                category_id=tc.id,
                name=tc.name,
                price_amount=tc.price.amount,
                price_currency=tc.price.currency,
                quota=tc.quota,
                remaining_quota=tc.remaining_quota,
                sales_start=tc.sales_start,
                sales_end=tc.sales_end,
                availability_status=availability,
            ))

        return EventDetail(
            event_id=event.id,
            name=event.name,
            description=event.description,
            location=event.location,
            start_date=event.start_date,
            end_date=event.end_date,
            organizer_id=event.organizer_id,
            status=event.status.value,
            ticket_categories=categories,
        )