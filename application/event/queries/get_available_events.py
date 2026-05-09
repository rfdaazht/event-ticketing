from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from domain.repositories.event_repository import IEventRepository


@dataclass
class GetAvailableEventsQuery:
    """Query data for fetching published events."""
    filter_date: date = None
    filter_location: str = None


@dataclass
class EventSummary:
    """Summary data for a single event in the list."""
    event_id: UUID
    name: str
    location: str
    start_date: date
    end_date: date
    lowest_price: Decimal
    currency: str


class GetAvailableEventsHandler:
    """
    Handles the GetAvailableEvents query.
    Returns all published events, with optional filters.
    """

    def __init__(self, event_repository: IEventRepository) -> None:
        self._event_repository = event_repository

    def handle(self, query: GetAvailableEventsQuery) -> list[EventSummary]:
        events = self._event_repository.find_all_published()

        # Apply optional filters
        if query.filter_date:
            events = [
                e for e in events
                if e.start_date == query.filter_date
            ]
        if query.filter_location:
            events = [
                e for e in events
                if query.filter_location.lower() in e.location.lower()
            ]

        result = []
        for event in events:
            # Get lowest price from active categories
            active_prices = [
                tc.price.amount
                for tc in event.active_categories
            ]
            lowest_price = min(active_prices) if active_prices else Decimal("0")
            currency = (
                event.active_categories[0].price.currency
                if event.active_categories else "IDR"
            )

            result.append(EventSummary(
                event_id=event.id,
                name=event.name,
                location=event.location,
                start_date=event.start_date,
                end_date=event.end_date,
                lowest_price=lowest_price,
                currency=currency,
            ))

        return result