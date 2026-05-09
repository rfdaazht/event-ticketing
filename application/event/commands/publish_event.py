from dataclasses import dataclass
from uuid import UUID

from domain.repositories.event_repository import IEventRepository


@dataclass
class PublishEventCommand:
    """Command data for publishing an event."""
    event_id: UUID
    organizer_id: UUID


@dataclass
class PublishEventResult:
    """Result returned after successfully publishing an event."""
    event_id: UUID
    status: str


class PublishEventHandler:
    """Handles the PublishEvent command."""

    def __init__(self, event_repository: IEventRepository) -> None:
        self._event_repository = event_repository

    def handle(self, command: PublishEventCommand) -> PublishEventResult:
        # Load aggregate from repository
        event = self._event_repository.find_by_id(command.event_id)
        if event is None:
            raise ValueError(f"Event {command.event_id} not found.")

        # Verify ownership
        if event.organizer_id != command.organizer_id:
            raise ValueError("Only the event organizer can publish this event.")

        # Business rules enforced inside event.publish()
        event.publish()

        # Persist updated aggregate
        self._event_repository.save(event)
        event.pull_domain_events()

        return PublishEventResult(
            event_id=event.id,
            status=event.status.value,
        )