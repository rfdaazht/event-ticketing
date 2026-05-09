from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from domain.event.aggregate import Event
from domain.repositories.event_repository import IEventRepository


@dataclass
class CreateEventCommand:
    """Command data for creating a new event."""
    organizer_id: UUID
    name: str
    description: str
    location: str
    start_date: date
    end_date: date
    max_capacity: int


@dataclass
class CreateEventResult:
    """Result returned after successfully creating an event."""
    event_id: UUID
    name: str
    status: str


class CreateEventHandler:
    """
    Handles the CreateEvent command.
    Orchestrates domain logic and persistence.
    """

    def __init__(self, event_repository: IEventRepository) -> None:
        self._event_repository = event_repository

    def handle(self, command: CreateEventCommand) -> CreateEventResult:
        # Create the aggregate via factory method
        # Business rules are enforced inside Event.create()
        event = Event.create(
            organizer_id=command.organizer_id,
            name=command.name,
            description=command.description,
            location=command.location,
            start_date=command.start_date,
            end_date=command.end_date,
            max_capacity=command.max_capacity,
        )

        # Persist the aggregate
        self._event_repository.save(event)

        # Pull and discard domain events for now
        # (will be dispatched in Week 12 infrastructure layer)
        event.pull_domain_events()

        return CreateEventResult(
            event_id=event.id,
            name=event.name,
            status=event.status.value,
        )