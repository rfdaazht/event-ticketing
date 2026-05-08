from abc import ABC, abstractmethod
from uuid import UUID

from domain.event.aggregate import Event


class IEventRepository(ABC):
    """
    Abstract interface for Event persistence.
    Defined in domain layer - implemented in infrastructure layer.
    """

    @abstractmethod
    def save(self, event: Event) -> None:
        """Save a new or updated Event aggregate."""
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, event_id: UUID) -> Event | None:
        """Return an Event by its ID, or None if not found."""
        raise NotImplementedError

    @abstractmethod
    def find_all_published(self) -> list[Event]:
        """Return all events with status Published."""
        raise NotImplementedError

    @abstractmethod
    def find_by_organizer(self, organizer_id: UUID) -> list[Event]:
        """Return all events created by a specific organizer."""
        raise NotImplementedError