from abc import ABC, abstractmethod
from uuid import UUID


class INotificationService(ABC):
    """
    Interface for sending notifications to users via email or WhatsApp.
    Defined in application layer — implemented in infrastructure layer.
    """

    @abstractmethod
    def send_booking_confirmation(
        self,
        customer_id: UUID,
        booking_id: UUID,
    ) -> None:
        """Send a booking confirmation notification to the customer."""
        raise NotImplementedError

    @abstractmethod
    def send_payment_confirmation(
        self,
        customer_id: UUID,
        booking_id: UUID,
    ) -> None:
        """Send a payment confirmation notification to the customer."""
        raise NotImplementedError

    @abstractmethod
    def send_ticket_issued(
        self,
        customer_id: UUID,
        booking_id: UUID,
        ticket_codes: list[str],
    ) -> None:
        """Send issued ticket codes to the customer after payment."""
        raise NotImplementedError

    @abstractmethod
    def send_refund_status(
        self,
        customer_id: UUID,
        refund_id: UUID,
        status: str,
    ) -> None:
        """Notify the customer about their refund status update."""
        raise NotImplementedError

    @abstractmethod
    def send_event_cancellation(
        self,
        customer_id: UUID,
        event_id: UUID,
    ) -> None:
        """Notify the customer that an event has been cancelled."""
        raise NotImplementedError