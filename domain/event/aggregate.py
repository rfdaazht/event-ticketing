from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from domain.shared.base import AggregateRoot, Entity
from domain.shared.value_objects import Money
from domain.shared.events import (
    EventCreated,
    EventPublished,
    EventCancelled,
    TicketCategoryCreated,
    TicketCategoryDisabled,
)
from domain.event.value_objects import EventStatus, TicketCategoryStatus


# ─ TicketCategory Entity

@dataclass(eq=False)
class TicketCategory(Entity):
    """
    Entity representing a type of ticket within an event.
    Examples: Regular, VIP, Early Bird.
    Belongs to the Event aggregate — accessed only through Event.
    """
    event_id: UUID = field(default=None)
    name: str = field(default="")
    price: Money = field(default=None)
    quota: int = field(default=0)
    sold: int = field(default=0)
    sales_start: date = field(default=None)
    sales_end: date = field(default=None)
    status: TicketCategoryStatus = field(default=TicketCategoryStatus.ACTIVE)

    @property
    def remaining_quota(self) -> int:
        return self.quota - self.sold

    @property
    def is_active(self) -> bool:
        return self.status == TicketCategoryStatus.ACTIVE

    def is_within_sales_period(self, today: date) -> bool:
        return self.sales_start <= today <= self.sales_end

    def disable(self) -> None:
        self.status = TicketCategoryStatus.DISABLED

    def reserve(self, quantity: int) -> None:
        """Reserve quota when a booking is created."""
        if quantity > self.remaining_quota:
            raise ValueError(
                f"Not enough quota. Requested: {quantity}, "
                f"Available: {self.remaining_quota}."
            )
        self.sold += quantity

    def release(self, quantity: int) -> None:
        """Release quota when a booking expires or is refunded."""
        self.sold = max(0, self.sold - quantity)


# ─ Event Aggregate Root

@dataclass(eq=False)
class Event(AggregateRoot):
    """
    Aggregate root for the Event domain.
    Manages the event lifecycle and its ticket categories.
    """
    organizer_id: UUID = field(default=None)
    name: str = field(default="")
    description: str = field(default="")
    location: str = field(default="")
    start_date: date = field(default=None)
    end_date: date = field(default=None)
    max_capacity: int = field(default=0)
    status: EventStatus = field(default=EventStatus.DRAFT)
    ticket_categories: list[TicketCategory] = field(default_factory=list)

    # ─ Factory Method

    @classmethod
    def create(
        cls,
        organizer_id: UUID,
        name: str,
        description: str,
        location: str,
        start_date: date,
        end_date: date,
        max_capacity: int,
    ) -> "Event":
        """
        The only valid way to create a new Event.
        Enforces all business rules on creation.
        """
        if end_date < start_date:
            raise ValueError("End date cannot be earlier than start date.")
        if max_capacity <= 0:
            raise ValueError("Maximum capacity must be greater than zero.")

        event = cls(
            organizer_id=organizer_id,
            name=name,
            description=description,
            location=location,
            start_date=start_date,
            end_date=end_date,
            max_capacity=max_capacity,
            status=EventStatus.DRAFT,
        )

        event._record_event(
            EventCreated(
                event_id=event.id,
                name=name,
                organizer_id=organizer_id,
            )
        )
        return event

    # ─ Properties

    @property
    def total_quota(self) -> int:
        return sum(tc.quota for tc in self.ticket_categories)

    @property
    def active_categories(self) -> list[TicketCategory]:
        return [tc for tc in self.ticket_categories if tc.is_active]

    # ─ Business Methods

    def add_ticket_category(
        self,
        name: str,
        price: Money,
        quota: int,
        sales_start: date,
        sales_end: date,
    ) -> TicketCategory:
        """Add a new ticket category to this event."""
        if self.status in (EventStatus.CANCELLED, EventStatus.COMPLETED):
            raise ValueError(
                f"Cannot add a ticket category to a {self.status.value} event."
            )
        if price.amount < Decimal("0"):
            raise ValueError("Ticket price cannot be negative.")
        if quota <= 0:
            raise ValueError("Ticket quota must be greater than zero.")
        if sales_end > self.start_date:
            raise ValueError(
                "Sales period must end before or on the event start date."
            )
        if self.total_quota + quota > self.max_capacity:
            raise ValueError(
                f"Total quota ({self.total_quota + quota}) exceeds "
                f"max capacity ({self.max_capacity})."
            )

        category = TicketCategory(
            event_id=self.id,
            name=name,
            price=price,
            quota=quota,
            sales_start=sales_start,
            sales_end=sales_end,
        )
        self.ticket_categories.append(category)

        self._record_event(
            TicketCategoryCreated(
                event_id=self.id,
                category_id=category.id,
                name=name,
            )
        )
        return category

    def disable_ticket_category(self, category_id: UUID) -> None:
        """Disable a ticket category so it can no longer be purchased."""
        if self.status == EventStatus.COMPLETED:
            raise ValueError("Cannot disable a category for a completed event.")

        category = self._find_category(category_id)
        category.disable()

        self._record_event(
            TicketCategoryDisabled(
                event_id=self.id,
                category_id=category_id,
            )
        )

    def publish(self) -> None:
        """Publish the event so customers can view and purchase tickets."""
        if self.status == EventStatus.CANCELLED:
            raise ValueError("A cancelled event cannot be published.")
        if self.status != EventStatus.DRAFT:
            raise ValueError("Only a draft event can be published.")
        if not self.active_categories:
            raise ValueError(
                "Event must have at least one active ticket category to be published."
            )
        if self.total_quota > self.max_capacity:
            raise ValueError(
                f"Total quota ({self.total_quota}) exceeds "
                f"max capacity ({self.max_capacity})."
            )

        self.status = EventStatus.PUBLISHED
        self._record_event(EventPublished(event_id=self.id))

    def cancel(self) -> None:
        """Cancel the event and stop all ticket sales."""
        if self.status == EventStatus.COMPLETED:
            raise ValueError("A completed event cannot be cancelled.")
        if self.status != EventStatus.PUBLISHED:
            raise ValueError("Only a published event can be cancelled.")

        self.status = EventStatus.CANCELLED
        self._record_event(EventCancelled(event_id=self.id))

    # ─ Private Helpers

    def _find_category(self, category_id: UUID) -> TicketCategory:
        for tc in self.ticket_categories:
            if tc.id == category_id:
                return tc
        raise ValueError(f"Ticket category {category_id} not found.")