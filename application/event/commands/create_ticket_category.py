from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from domain.shared.value_objects import Money
from domain.repositories.event_repository import IEventRepository


@dataclass
class CreateTicketCategoryCommand:
    """Command data for adding a ticket category to an event."""
    event_id: UUID
    organizer_id: UUID
    name: str
    price_amount: Decimal
    price_currency: str
    quota: int
    sales_start: date
    sales_end: date


@dataclass
class CreateTicketCategoryResult:
    """Result returned after successfully creating a ticket category."""
    category_id: UUID
    name: str
    quota: int


class CreateTicketCategoryHandler:
    """Handles the CreateTicketCategory command."""

    def __init__(self, event_repository: IEventRepository) -> None:
        self._event_repository = event_repository

    def handle(self, command: CreateTicketCategoryCommand) -> CreateTicketCategoryResult:
        event = self._event_repository.find_by_id(command.event_id)
        if event is None:
            raise ValueError(f"Event {command.event_id} not found.")

        if event.organizer_id != command.organizer_id:
            raise ValueError("Only the event organizer can add ticket categories.")

        price = Money(command.price_amount, command.price_currency)

        category = event.add_ticket_category(
            name=command.name,
            price=price,
            quota=command.quota,
            sales_start=command.sales_start,
            sales_end=command.sales_end,
        )

        self._event_repository.save(event)
        event.pull_domain_events()

        return CreateTicketCategoryResult(
            category_id=category.id,
            name=category.name,
            quota=category.quota,
        )