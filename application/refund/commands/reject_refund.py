from dataclasses import dataclass
from uuid import UUID

from domain.repositories.refund_repository import IRefundRepository


@dataclass
class RejectRefundCommand:
    """Command data for rejecting a refund request."""
    refund_id: UUID
    organizer_id: UUID
    rejection_reason: str


@dataclass
class RejectRefundResult:
    """Result returned after successfully rejecting a refund."""
    refund_id: UUID
    status: str
    rejection_reason: str


class RejectRefundHandler:
    """Handles the RejectRefund command."""

    def __init__(self, refund_repository: IRefundRepository) -> None:
        self._refund_repository = refund_repository

    def handle(self, command: RejectRefundCommand) -> RejectRefundResult:
        refund = self._refund_repository.find_by_id(command.refund_id)
        if refund is None:
            raise ValueError(f"Refund {command.refund_id} not found.")

        # Business rules enforced inside reject()
        refund.reject(rejection_reason=command.rejection_reason)
        self._refund_repository.save(refund)
        refund.pull_domain_events()

        return RejectRefundResult(
            refund_id=refund.id,
            status=refund.status.value,
            rejection_reason=refund.rejection_reason,
        )