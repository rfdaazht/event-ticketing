"""
Presentation Layer — Refund Routes
FastAPI router untuk semua endpoint Refund.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.refund.commands.request_refund import RequestRefundCommand, RequestRefundHandler
from application.refund.commands.approve_refund import ApproveRefundCommand, ApproveRefundHandler
from application.refund.commands.reject_refund import RejectRefundCommand, RejectRefundHandler
from application.refund.commands.mark_refund_paid_out import (
    MarkRefundPaidOutCommand,
    MarkRefundPaidOutHandler,
)
from application.refund.queries.get_refund_detail import GetRefundDetailQuery, GetRefundDetailHandler

from infrastructure.database.connection import get_db
from infrastructure.repositories.refund_repository import PostgreSQLRefundRepository
from infrastructure.repositories.booking_repository import PostgreSQLBookingRepository
from infrastructure.repositories.ticket_repository import PostgreSQLTicketRepository
from infrastructure.repositories.event_repository import PostgreSQLEventRepository

from presentation.api.schemas.refund_schemas import (
    RequestRefundRequest,
    RequestRefundResponse,
    ApproveRefundRequest,
    ApproveRefundResponse,
    RejectRefundRequest,
    RejectRefundResponse,
    MarkRefundPaidOutRequest,
    MarkRefundPaidOutResponse,
    RefundResponse,
)

router = APIRouter(prefix="/refunds", tags=["Refunds"])


# ─────────────────────────────────────────────────────────
# Refund Endpoints
# ─────────────────────────────────────────────────────────

@router.post(
    "/bookings/{booking_id}/request",
    response_model=RequestRefundResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Request a refund for a paid booking",
)
def request_refund(
    booking_id: UUID,
    body: RequestRefundRequest,
    db: Session = Depends(get_db),
) -> RequestRefundResponse:
    """Customer mengajukan refund untuk booking yang sudah dibayar."""
    handler = RequestRefundHandler(
        booking_repository=PostgreSQLBookingRepository(db),
        event_repository=PostgreSQLEventRepository(db),
        ticket_repository=PostgreSQLTicketRepository(db),
        refund_repository=PostgreSQLRefundRepository(db),
    )
    command = RequestRefundCommand(
        booking_id=booking_id,
        customer_id=body.customer_id,
        reason=body.reason,
    )
    try:
        result = handler.handle(command)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return RequestRefundResponse(
        refund_id=result.refund_id,
        booking_id=result.booking_id,
        status=result.status,
    )


@router.get(
    "/{refund_id}",
    response_model=RefundResponse,
    summary="Get refund detail",
)
def get_refund_detail(
    refund_id: UUID,
    customer_id: UUID,
    db: Session = Depends(get_db),
) -> RefundResponse:
    """Customer melihat detail status refund miliknya."""
    handler = GetRefundDetailHandler(PostgreSQLRefundRepository(db))
    query = GetRefundDetailQuery(refund_id=refund_id, customer_id=customer_id)
    try:
        result = handler.handle(query)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return RefundResponse(
        refund_id=result.refund_id,
        booking_id=result.booking_id,
        customer_id=result.customer_id,
        amount=result.amount,
        currency=result.currency,
        status=result.status,
        reason=result.reason,
        rejection_reason=result.rejection_reason,
        payment_reference=result.payment_reference,
        requested_at=result.requested_at,
        resolved_at=result.resolved_at,
    )


@router.post(
    "/{refund_id}/approve",
    response_model=ApproveRefundResponse,
    summary="Approve a refund request",
)
def approve_refund(
    refund_id: UUID,
    body: ApproveRefundRequest,
    db: Session = Depends(get_db),
) -> ApproveRefundResponse:
    """Event Organizer menyetujui pengajuan refund dari customer."""
    handler = ApproveRefundHandler(
        refund_repository=PostgreSQLRefundRepository(db),
        booking_repository=PostgreSQLBookingRepository(db),
        ticket_repository=PostgreSQLTicketRepository(db),
    )
    command = ApproveRefundCommand(refund_id=refund_id, organizer_id=body.organizer_id)
    try:
        result = handler.handle(command)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return ApproveRefundResponse(refund_id=result.refund_id, status=result.status)


@router.post(
    "/{refund_id}/reject",
    response_model=RejectRefundResponse,
    summary="Reject a refund request",
)
def reject_refund(
    refund_id: UUID,
    body: RejectRefundRequest,
    db: Session = Depends(get_db),
) -> RejectRefundResponse:
    """Event Organizer menolak pengajuan refund dengan menyertakan alasan penolakan."""
    handler = RejectRefundHandler(PostgreSQLRefundRepository(db))
    command = RejectRefundCommand(
        refund_id=refund_id,
        organizer_id=body.organizer_id,
        rejection_reason=body.rejection_reason,
    )
    try:
        result = handler.handle(command)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return RejectRefundResponse(
        refund_id=result.refund_id,
        status=result.status,
        rejection_reason=result.rejection_reason,
    )


@router.post(
    "/{refund_id}/mark-paid-out",
    response_model=MarkRefundPaidOutResponse,
    summary="Mark a refund as paid out (admin only)",
)
def mark_refund_paid_out(
    refund_id: UUID,
    body: MarkRefundPaidOutRequest,
    db: Session = Depends(get_db),
) -> MarkRefundPaidOutResponse:
    """System Admin menandai refund sudah dicairkan ke rekening customer."""
    handler = MarkRefundPaidOutHandler(PostgreSQLRefundRepository(db))
    command = MarkRefundPaidOutCommand(
        refund_id=refund_id,
        admin_id=body.admin_id,
        payment_reference=body.payment_reference,
    )
    try:
        result = handler.handle(command)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return MarkRefundPaidOutResponse(
        refund_id=result.refund_id,
        status=result.status,
        payment_reference=result.payment_reference,
    )
