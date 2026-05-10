from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from domain.repositories.refund_repository import IRefundRepository


@dataclass
class GetRefundDetailQuery:
    """Query data for fetching a single refund's details."""
    refund_id: UUID
    customer_id: UUID


@dataclass
class RefundDetail:
    """Full detail data for a single refund."""
    refund_id: UUID
    booking_id: UUID
    customer_id: UUID
    amount: Decimal
    currency: str
    status: str
    reason: str
    rejection_reason: str | None
    payment_reference: str | None
    requested_at: datetime
    resolved_at: datetime | None


class GetRefundDetailHandler:
    """Handles the GetRefundDetail query."""

    def __init__(self, refund_repository: IRefundRepository) -> None:
        self._refund_repository = refund_repository

    def handle(self, query: GetRefundDetailQuery) -> RefundDetail:
        refund = self._refund_repository.find_by_id(query.refund_id)
        if refund is None:
            raise ValueError(f"Refund {query.refund_id} not found.")
        if refund.customer_id != query.customer_id:
            raise ValueError("This refund does not belong to this customer.")

        return RefundDetail(
            refund_id=refund.id,
            booking_id=refund.booking_id,
            customer_id=refund.customer_id,
            amount=refund.amount.amount,
            currency=refund.amount.currency,
            status=refund.status.value,
            reason=refund.reason,
            rejection_reason=refund.rejection_reason,
            payment_reference=refund.payment_reference,
            requested_at=refund.requested_at,
            resolved_at=refund.resolved_at,
        )