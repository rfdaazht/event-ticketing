"""
Presentation Layer — Ticket Routes
FastAPI router untuk semua endpoint Ticket & Check-in.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.ticket.commands.check_in_ticket import (
    CheckInTicketCommand,
    CheckInTicketHandler,
    TicketNotFoundError,
    EventCancelledError,
)
from application.ticket.queries.get_purchased_tickets import (
    GetPurchasedTicketsQuery,
    GetPurchasedTicketsHandler,
)
from domain.ticket.aggregate import (
    TicketAlreadyCheckedInError,
    TicketCancelledError,
    TicketEventMismatchError,
    TicketOutsideCheckInWindowError,
)

from infrastructure.database.connection import get_db
from infrastructure.repositories.ticket_repository import PostgreSQLTicketRepository
from infrastructure.repositories.event_repository import PostgreSQLEventRepository

from presentation.api.schemas.ticket_schemas import (
    CheckInTicketRequest,
    CheckInTicketResponse,
    TicketResponse,
)

# ─────────────────────────────────────────────────────────
# Customer Ticket Router
# ─────────────────────────────────────────────────────────

customer_router = APIRouter(prefix="/tickets", tags=["Tickets"])


@customer_router.get(
    "/",
    response_model=list[TicketResponse],
    summary="Get all purchased tickets for a customer",
)
def get_purchased_tickets(
    customer_id: UUID,
    db: Session = Depends(get_db),
) -> list[TicketResponse]:
    """Customer melihat semua tiket yang sudah dimiliki."""
    handler = GetPurchasedTicketsHandler(PostgreSQLTicketRepository(db))
    query = GetPurchasedTicketsQuery(customer_id=customer_id)
    results = handler.handle(query)

    return [
        TicketResponse(
            ticket_id=t.ticket_id,
            ticket_code=t.ticket_code,
            event_id=t.event_id,
            ticket_category_id=t.ticket_category_id,
            status=t.status,
            issued_at=t.issued_at,
            checked_in_at=t.checked_in_at,
        )
        for t in results
    ]


# ─────────────────────────────────────────────────────────
# Gate Officer Check-in Router
# ─────────────────────────────────────────────────────────

gate_router = APIRouter(prefix="/events/{event_id}/check-in", tags=["Check-in"])


@gate_router.post(
    "/",
    response_model=CheckInTicketResponse,
    summary="Check in a ticket at the event gate",
)
def check_in_ticket(
    event_id: UUID,
    body: CheckInTicketRequest,
    db: Session = Depends(get_db),
) -> CheckInTicketResponse:
    """
    Gate Officer melakukan scan dan validasi tiket saat event berlangsung.

    Error responses:
    - 404: Ticket code tidak valid / tidak ditemukan
    - 410: Event telah dibatalkan
    - 409: Tiket sudah pernah di-check-in
    - 403: Tiket bukan untuk event ini
    - 422: Di luar window check-in event
    """
    handler = CheckInTicketHandler(
        ticket_repository=PostgreSQLTicketRepository(db),
        event_repository=PostgreSQLEventRepository(db),
    )
    command = CheckInTicketCommand(
        ticket_code=body.ticket_code,
        event_id=event_id,
        gate_officer_id=body.gate_officer_id,
    )
    try:
        result = handler.handle(command)
    except TicketNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except EventCancelledError as exc:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=str(exc))
    except TicketAlreadyCheckedInError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except TicketEventMismatchError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except TicketOutsideCheckInWindowError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except (TicketCancelledError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return CheckInTicketResponse(
        ticket_id=result.ticket_id,
        ticket_code=result.ticket_code,
        status=result.status,
        checked_in_at=result.checked_in_at,
    )
