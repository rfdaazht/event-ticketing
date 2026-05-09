from dataclasses import dataclass
from uuid import UUID

from domain.repositories.event_repository import IEventRepository


@dataclass
class CancelEventCommand:
    """Command data for cancelling an event."""
    event_id: UUID
    organizer_id: UUID


@dataclass
class CancelEventResult:
    """Result returned after successfully cancelling an event."""
    event_id: UUID
    status: str


class CancelEventHandler:
    """Handles the CancelEvent command."""

    def __init__(self, event_repository: IEventRepository) -> None:
        self._event_repository = event_repository

    def handle(self, command: CancelEventCommand) -> CancelEventResult:
        event = self._event_repository.find_by_id(command.event_id)
        if event is None:
            raise ValueError(f"Event {command.event_id} not found.")

        if event.organizer_id != command.organizer_id:
            raise ValueError("Only the event organizer can cancel this event.")

        event.cancel()

        self._event_repository.save(event)
        event.pull_domain_events()

        return CancelEventResult(
            event_id=event.id,
            status=event.status.value,
        )