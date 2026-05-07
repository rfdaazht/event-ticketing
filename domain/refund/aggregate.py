from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from domain.shared.base import AggregateRoot
from domain.shared.value_objects import Money
from domain.shared.events import (
    RefundRequested,
    RefundApproved,
    RefundRejected,
    RefundPaidOut,
)
from domain.refund.value_objects import RefundStatus


@dataclass(eq=False)
class Refund(AggregateRoot):
    """
    Aggregate root for the Refund domain.
    Manages the lifecycle of a refund request from a customer.
    """
    booking_id: UUID = field(default=None)
    customer_id: UUID = field(default=None)
    amount: Money = field(default=None)
    status: RefundStatus = field(default=RefundStatus.REQUESTED)
    reason: str = field(default="")
    rejection_reason: str = field(default=None)
    payment_reference: str = field(default=None)
    requested_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: datetime = field(default=None)

    # ─ Factory Method

    @classmethod
    def request(
        cls,
        booking_id: UUID,
        customer_id: UUID,
        amount: Money,
        reason: str = "",
    ) -> "Refund":
        """
        The only valid way to create a new Refund request.
        Called after validating that the booking is eligible for refund.
        """
        refund = cls(
            booking_id=booking_id,
            customer_id=customer_id,
            amount=amount,
            reason=reason,
            status=RefundStatus.REQUESTED,
        )

        refund._record_event(
            RefundRequested(
                refund_id=refund.id,
                booking_id=booking_id,
                customer_id=customer_id,
            )
        )
        return refund

    # ─ Business Methods

    def approve(self) -> None:
        """
        Approve this refund request.
        Called by the Event Organizer.
        """
        if self.status != RefundStatus.REQUESTED:
            raise ValueError(
                f"Only a requested refund can be approved. "
                f"Current status: {self.status.value}."
            )

        self.status = RefundStatus.APPROVED
        self.resolved_at = datetime.utcnow()

        self._record_event(
            RefundApproved(
                refund_id=self.id,
                booking_id=self.booking_id,
            )
        )

    def reject(self, rejection_reason: str) -> None:
        """
        Reject this refund request.
        Called by the Event Organizer.
        A rejection reason must always be provided.
        """
        if self.status != RefundStatus.REQUESTED:
            raise ValueError(
                f"Only a requested refund can be rejected. "
                f"Current status: {self.status.value}."
            )
        if not rejection_reason or not rejection_reason.strip():
            raise ValueError("A rejection reason must be provided.")

        self.status = RefundStatus.REJECTED
        self.rejection_reason = rejection_reason
        self.resolved_at = datetime.utcnow()

        self._record_event(
            RefundRejected(
                refund_id=self.id,
                booking_id=self.booking_id,
                reason=rejection_reason,
            )
        )

    def mark_as_paid_out(self, payment_reference: str) -> None:
        """
        Mark this refund as paid out.
        Called by the System Admin after disbursement is confirmed.
        """
        if self.status != RefundStatus.APPROVED:
            raise ValueError(
                f"Only an approved refund can be marked as paid out. "
                f"Current status: {self.status.value}."
            )
        if not payment_reference or not payment_reference.strip():
            raise ValueError("A payment reference must be provided.")

        self.status = RefundStatus.PAID_OUT
        self.payment_reference = payment_reference
        self.resolved_at = datetime.utcnow()

        self._record_event(
            RefundPaidOut(
                refund_id=self.id,
                payment_reference=payment_reference,
            )
        )

    # ─ Properties

    @property
    def is_resolved(self) -> bool:
        return self.status in (
            RefundStatus.APPROVED,
            RefundStatus.REJECTED,
            RefundStatus.PAID_OUT,
        )