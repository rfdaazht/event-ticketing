"""
Presentation Layer — Refund API Schemas
Pydantic models untuk request body dan response Refund endpoints.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────
# Request Schemas
# ─────────────────────────────────────────────────────────

class RequestRefundRequest(BaseModel):
    customer_id: UUID
    reason: str = Field(default="")


class ApproveRefundRequest(BaseModel):
    organizer_id: UUID


class RejectRefundRequest(BaseModel):
    organizer_id: UUID
    rejection_reason: str = Field(..., min_length=1)


class MarkRefundPaidOutRequest(BaseModel):
    admin_id: UUID
    payment_reference: str = Field(..., min_length=1)


# ─────────────────────────────────────────────────────────
# Response Schemas
# ─────────────────────────────────────────────────────────

class RefundResponse(BaseModel):
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

    model_config = {"from_attributes": True}


class RequestRefundResponse(BaseModel):
    refund_id: UUID
    booking_id: UUID
    status: str


class ApproveRefundResponse(BaseModel):
    refund_id: UUID
    status: str


class RejectRefundResponse(BaseModel):
    refund_id: UUID
    status: str
    rejection_reason: str


class MarkRefundPaidOutResponse(BaseModel):
    refund_id: UUID
    status: str
    payment_reference: str
