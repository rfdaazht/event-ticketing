from abc import ABC, abstractmethod
from uuid import UUID

from domain.ticket.aggregate import Ticket


class ITicketRepository(ABC):
    """
    Abstract interface for Ticket persistence.
    Defined in domain layer - implemented in infrastructure layer.
    """

    @abstractmethod
    def save(self, ticket: Ticket) -> None:
        """Save a new or updated Ticket aggregate."""
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, ticket_id: UUID) -> Ticket | None:
        """Return a Ticket by its ID, or None if not found."""
        raise NotImplementedError

    @abstractmethod
    def find_by_code(self, ticket_code: str) -> Ticket | None:
        """Return a Ticket by its unique ticket code, or None if not found."""
        raise NotImplementedError

    @abstractmethod
    def find_by_booking(self, booking_id: UUID) -> list[Ticket]:
        """Return all tickets issued for a specific booking."""
        raise NotImplementedError

    @abstractmethod
    def find_by_customer(self, customer_id: UUID) -> list[Ticket]:
        """Return all tickets owned by a specific customer."""
        raise NotImplementedError