from dataclasses import dataclass
from uuid import UUID

from domain.repositories.refund_repository import IRefundRepository


@dataclass
class MarkRefundPaidOutCommand:
    """Command data for marking a refund as paid out."""
    refund_id: UUID
    admin_id: UUID
    payment_reference: str


@dataclass
class MarkRefundPaidOutResult:
    """Result returned after successfully marking a refund as paid out."""
    refund_id: UUID
    status: str
    payment_reference: str


class MarkRefundPaidOutHandler:
    """
    Handles the MarkRefundPaidOut command.
    Called by System Admin after disbursement is confirmed.
    """

    def __init__(self, refund_repository: IRefundRepository) -> None:
        self._refund_repository = refund_repository

    def handle(self, command: MarkRefundPaidOutCommand) -> MarkRefundPaidOutResult:
        refund = self._refund_repository.find_by_id(command.refund_id)
        if refund is None:
            raise ValueError(f"Refund {command.refund_id} not found.")

        # Business rules enforced inside mark_as_paid_out()
        refund.mark_as_paid_out(payment_reference=command.payment_reference)
        self._refund_repository.save(refund)
        refund.pull_domain_events()

        return MarkRefundPaidOutResult(
            refund_id=refund.id,
            status=refund.status.value,
            payment_reference=refund.payment_reference,
        )