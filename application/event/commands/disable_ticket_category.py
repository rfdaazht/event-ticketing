from dataclasses import dataclass
from uuid import UUID

from domain.repositories.event_repository import IEventRepository


@dataclass
class DisableTicketCategoryCommand:
    """Command data for disabling a ticket category."""
    event_id: UUID
    category_id: UUID
    organizer_id: UUID


@dataclass
class DisableTicketCategoryResult:
    """Result returned after successfully disabling a ticket category."""
    category_id: UUID
    status: str


class DisableTicketCategoryHandler:
    """Handles the DisableTicketCategory command."""

    def __init__(self, event_repository: IEventRepository) -> None:
        self._event_repository = event_repository

    def handle(self, command: DisableTicketCategoryCommand) -> DisableTicketCategoryResult:
        event = self._event_repository.find_by_id(command.event_id)
        if event is None:
            raise ValueError(f"Event {command.event_id} not found.")

        if event.organizer_id != command.organizer_id:
            raise ValueError("Only the event organizer can disable ticket categories.")

        event.disable_ticket_category(command.category_id)

        self._event_repository.save(event)
        event.pull_domain_events()

        return DisableTicketCategoryResult(
            category_id=command.category_id,
            status="disabled",
        )