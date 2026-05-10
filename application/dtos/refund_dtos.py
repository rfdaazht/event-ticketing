from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


# ─ Request DTOs

@dataclass
class RequestRefundRequest:
    customer_id: UUID
    reason: str = ""


@dataclass
class ApproveRefundRequest:
    organizer_id: UUID


@dataclass
class RejectRefundRequest:
    organizer_id: UUID
    rejection_reason: str


@dataclass
class MarkRefundPaidOutRequest:
    admin_id: UUID
    payment_reference: str


# ─ Response DTOs

@dataclass
class RefundResponse:
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