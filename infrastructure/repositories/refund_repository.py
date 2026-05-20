from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from domain.refund.aggregate import Refund
from domain.refund.value_objects import RefundStatus
from domain.shared.value_objects import Money
from domain.repositories.refund_repository import IRefundRepository
from infrastructure.database.models import RefundModel


class PostgreSQLRefundRepository(IRefundRepository):
    """Concrete implementation of IRefundRepository using PostgreSQL."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, refund: Refund) -> None:
        existing = self._db.query(RefundModel).filter_by(id=refund.id).first()
        if existing:
            self._update_model(existing, refund)
        else:
            self._db.add(self._to_model(refund))
        self._db.commit()

    def find_by_id(self, refund_id: UUID) -> Refund | None:
        model = self._db.query(RefundModel).filter_by(id=refund_id).first()
        return self._to_domain(model) if model else None

    def find_by_booking(self, booking_id: UUID) -> Refund | None:
        model = self._db.query(RefundModel).filter_by(booking_id=booking_id).first()
        return self._to_domain(model) if model else None

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _to_model(self, refund: Refund) -> RefundModel:
        return RefundModel(
            id=refund.id,
            booking_id=refund.booking_id,
            customer_id=refund.customer_id,
            amount=float(refund.amount.amount),
            currency=refund.amount.currency,
            status=refund.status.value,
            reason=refund.reason,
            rejection_reason=refund.rejection_reason,
            payment_reference=refund.payment_reference,
            requested_at=refund.requested_at,
            resolved_at=refund.resolved_at,
        )

    def _update_model(self, model: RefundModel, refund: Refund) -> None:
        model.status = refund.status.value
        model.rejection_reason = refund.rejection_reason
        model.payment_reference = refund.payment_reference
        model.resolved_at = refund.resolved_at

    def _to_domain(self, model: RefundModel) -> Refund:
        return Refund(
            id=model.id,
            booking_id=model.booking_id,
            customer_id=model.customer_id,
            amount=Money(Decimal(str(model.amount)), model.currency),
            status=RefundStatus(model.status),
            reason=model.reason or "",
            rejection_reason=model.rejection_reason,
            payment_reference=model.payment_reference,
            requested_at=model.requested_at,
            resolved_at=model.resolved_at,
        )