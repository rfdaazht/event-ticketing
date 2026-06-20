"""
Presentation Layer — Booking Routes
FastAPI router untuk semua endpoint Booking.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.booking.commands.create_booking import CreateBookingCommand, CreateBookingHandler
from application.booking.commands.pay_booking import PayBookingCommand, PayBookingHandler
from application.booking.commands.expire_booking import ExpireBookingCommand, ExpireBookingHandler
from application.booking.queries.get_booking_detail import (
    GetBookingDetailQuery,
    GetBookingDetailHandler,
)

from infrastructure.database.connection import get_db
from infrastructure.repositories.booking_repository import PostgreSQLBookingRepository
from infrastructure.repositories.event_repository import PostgreSQLEventRepository
from infrastructure.repositories.ticket_repository import PostgreSQLTicketRepository
from infrastructure.services.services import (
    DummyPaymentGatewayService,
    DummyNotificationService,
)

from presentation.api.schemas.booking_schemas import (
    CreateBookingRequest,
    CreateBookingResponse,
    PayBookingRequest,
    PayBookingResponse,
    BookingResponse,
    ExpireBookingResponse,
)

router = APIRouter(prefix="/events/{event_id}/bookings", tags=["Bookings"])


# ─────────────────────────────────────────────────────────
# Booking Endpoints
# ─────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=CreateBookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a booking for an event",
)
def create_booking(
    event_id: UUID,
    body: CreateBookingRequest,
    db: Session = Depends(get_db),
) -> CreateBookingResponse:
    """Customer melakukan pemesanan tiket untuk sebuah event yang sudah dipublish."""
    handler = CreateBookingHandler(
        event_repository=PostgreSQLEventRepository(db),
        booking_repository=PostgreSQLBookingRepository(db),
    )
    command = CreateBookingCommand(
        customer_id=body.customer_id,
        event_id=event_id,
        ticket_category_id=body.ticket_category_id,
        quantity=body.quantity,
    )
    try:
        result = handler.handle(command)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return CreateBookingResponse(
        booking_id=result.booking_id,
        total_price_amount=result.total_price_amount,
        total_price_currency=result.total_price_currency,
        payment_deadline=result.payment_deadline,
        status=result.status,
    )


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
    summary="Get booking detail",
)
def get_booking_detail(
    event_id: UUID,
    booking_id: UUID,
    customer_id: UUID,
    db: Session = Depends(get_db),
) -> BookingResponse:
    """Customer melihat detail pemesanan miliknya."""
    handler = GetBookingDetailHandler(PostgreSQLBookingRepository(db))
    query = GetBookingDetailQuery(booking_id=booking_id, customer_id=customer_id)
    try:
        result = handler.handle(query)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return BookingResponse(
        booking_id=result.booking_id,
        customer_id=result.customer_id,
        event_id=result.event_id,
        ticket_category_id=result.ticket_category_id,
        quantity=result.quantity,
        total_price_amount=result.total_price_amount,
        total_price_currency=result.total_price_currency,
        status=result.status,
        payment_deadline=result.payment_deadline,
        created_at=result.created_at,
    )


@router.post(
    "/{booking_id}/pay",
    response_model=PayBookingResponse,
    summary="Pay for a booking",
)
def pay_booking(
    event_id: UUID,
    booking_id: UUID,
    body: PayBookingRequest,
    db: Session = Depends(get_db),
) -> PayBookingResponse:
    """Customer melakukan pembayaran untuk booking yang masih pending."""
    handler = PayBookingHandler(
        booking_repository=PostgreSQLBookingRepository(db),
        ticket_repository=PostgreSQLTicketRepository(db),
        payment_gateway=DummyPaymentGatewayService(),
        notification_service=DummyNotificationService(),
    )
    command = PayBookingCommand(
        booking_id=booking_id,
        customer_id=body.customer_id,
        amount_paid=body.amount_paid,
        currency=body.currency,
    )
    try:
        result = handler.handle(command)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return PayBookingResponse(
        booking_id=result.booking_id,
        status=result.status,
        tickets_issued=result.tickets_issued,
    )


@router.post(
    "/{booking_id}/expire",
    response_model=ExpireBookingResponse,
    summary="Expire a booking (system use)",
)
def expire_booking(
    event_id: UUID,
    booking_id: UUID,
    db: Session = Depends(get_db),
) -> ExpireBookingResponse:
    """
    Endpoint untuk sistem/scheduler yang secara otomatis mengexpire booking
    yang melewati deadline pembayaran.
    """
    handler = ExpireBookingHandler(
        booking_repository=PostgreSQLBookingRepository(db),
        event_repository=PostgreSQLEventRepository(db),
    )
    command = ExpireBookingCommand(booking_id=booking_id)
    try:
        result = handler.handle(command)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return ExpireBookingResponse(booking_id=result.booking_id, status=result.status)
