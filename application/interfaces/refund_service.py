from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class RefundResult:
    """Result returned after a refund disbursement attempt."""
    success: bool
    payment_reference: str
    message: str = ""


class IRefundPaymentService(ABC):
    """
    Interface for disbursing refund payouts to customer bank accounts.
    Defined in application layer — implemented in infrastructure layer.
    """

    @abstractmethod
    def process_refund(
        self,
        refund_id: UUID,
        customer_id: UUID,
        amount: Decimal,
        currency: str,
    ) -> RefundResult:
        """
        Disburse a refund to the customer's bank account.
        Returns a RefundResult with a payment reference on success.
        """
        raise NotImplementedError