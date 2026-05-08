from abc import ABC, abstractmethod
from uuid import UUID

from domain.refund.aggregate import Refund


class IRefundRepository(ABC):
    """
    Abstract interface for Refund persistence.
    Defined in domain layer - implemented in infrastructure layer.
    """

    @abstractmethod
    def save(self, refund: Refund) -> None:
        """Save a new or updated Refund aggregate."""
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, refund_id: UUID) -> Refund | None:
        """Return a Refund by its ID, or None if not found."""
        raise NotImplementedError

    @abstractmethod
    def find_by_booking(self, booking_id: UUID) -> Refund | None:
        """Return the refund associated with a specific booking."""
        raise NotImplementedError