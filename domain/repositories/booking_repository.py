from abc import ABC, abstractmethod
from uuid import UUID

from domain.booking.aggregate import Booking


class IBookingRepository(ABC):
    """
    Abstract interface for Booking persistence.
    Defined in domain layer - implemented in infrastructure layer.
    """

    @abstractmethod
    def save(self, booking: Booking) -> None:
        """Save a new or updated Booking aggregate."""
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, booking_id: UUID) -> Booking | None:
        """Return a Booking by its ID, or None if not found."""
        raise NotImplementedError

    @abstractmethod
    def find_by_customer_and_event(
        self, customer_id: UUID, event_id: UUID
    ) -> Booking | None:
        """
        Return an active booking for a specific customer and event.
        Used to enforce: one active booking per customer per event.
        """
        raise NotImplementedError

    @abstractmethod
    def find_expired_pending(self) -> list[Booking]:
        """
        Return all bookings with status PendingPayment
        whose payment deadline has passed.
        Used by the system to auto-expire unpaid bookings.
        """
        raise NotImplementedError