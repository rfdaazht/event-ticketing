from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from domain.repositories.event_repository import IEventRepository
from domain.repositories.booking_repository import IBookingRepository


@dataclass
class GetSalesReportQuery:
    """Query data for fetching a sales report for an event."""
    event_id: UUID
    organizer_id: UUID


@dataclass
class CategorySalesDetail:
    """Sales breakdown per ticket category."""
    category_id: UUID
    name: str
    quota: int
    sold: int
    remaining: int


@dataclass
class SalesReport:
    """Full sales report for an event."""
    event_id: UUID
    event_name: str
    total_revenue: Decimal
    currency: str
    booking_count_pending: int
    booking_count_paid: int
    booking_count_expired: int
    booking_count_refunded: int
    categories: list[CategorySalesDetail]


class GetSalesReportHandler:
    """Handles the GetSalesReport query."""

    def __init__(
        self,
        event_repository: IEventRepository,
        booking_repository: IBookingRepository,
    ) -> None:
        self._event_repository = event_repository
        self._booking_repository = booking_repository

    def handle(self, query: GetSalesReportQuery) -> SalesReport:
        event = self._event_repository.find_by_id(query.event_id)
        if event is None:
            raise ValueError(f"Event {query.event_id} not found.")
        if event.organizer_id != query.organizer_id:
            raise ValueError("Only the event organizer can view this report.")

        bookings = self._booking_repository.find_by_event(query.event_id)

        # Count bookings by status
        pending  = sum(1 for b in bookings if b.status.value == "pending_payment")
        paid     = sum(1 for b in bookings if b.status.value == "paid")
        expired  = sum(1 for b in bookings if b.status.value == "expired")
        refunded = sum(1 for b in bookings if b.status.value == "refunded")

        # Total revenue from paid bookings only
        currency = "IDR"
        total_revenue = sum(
            b.total_price.amount
            for b in bookings
            if b.status.value == "paid"
        )
        if bookings:
            currency = bookings[0].total_price.currency

        # Category breakdown
        categories = [
            CategorySalesDetail(
                category_id=tc.id,
                name=tc.name,
                quota=tc.quota,
                sold=tc.sold,
                remaining=tc.remaining_quota,
            )
            for tc in event.ticket_categories
        ]

        return SalesReport(
            event_id=event.id,
            event_name=event.name,
            total_revenue=total_revenue,
            currency=currency,
            booking_count_pending=pending,
            booking_count_paid=paid,
            booking_count_expired=expired,
            booking_count_refunded=refunded,
            categories=categories,
        )