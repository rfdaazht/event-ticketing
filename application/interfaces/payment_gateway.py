from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class PaymentResult:
    """Result returned after a payment attempt."""
    success: bool
    transaction_id: str
    message: str = ""


class IPaymentGatewayService(ABC):
    """
    Interface for processing booking payments via external payment gateway.
    Defined in application layer — implemented in infrastructure layer.
    """

    @abstractmethod
    def process_payment(
        self,
        booking_id: UUID,
        customer_id: UUID,
        amount: Decimal,
        currency: str,
    ) -> PaymentResult:
        """
        Process a payment for a booking.
        Returns a PaymentResult indicating success or failure.
        """
        raise NotImplementedError