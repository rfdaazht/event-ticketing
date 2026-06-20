"""
Presentation Layer — Event Routes
FastAPI router untuk semua endpoint Event & TicketCategory.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.event.commands.create_event import CreateEventCommand, CreateEventHandler
from application.event.commands.publish_event import PublishEventCommand, PublishEventHandler
from application.event.commands.cancel_event import CancelEventCommand, CancelEventHandler
from application.event.commands.create_ticket_category import (
    CreateTicketCategoryCommand,
    CreateTicketCategoryHandler,
)
from application.event.commands.disable_ticket_category import (
    DisableTicketCategoryCommand,
    DisableTicketCategoryHandler,
)
from application.event.queries.get_available_events import (
    GetAvailableEventsQuery,
    GetAvailableEventsHandler,
)
from application.event.queries.get_event_detail import GetEventDetailQuery, GetEventDetailHandler
from application.event.queries.get_participants import GetParticipantsQuery, GetParticipantsHandler
from application.event.queries.get_sales_report import GetSalesReportQuery, GetSalesReportHandler

from infrastructure.database.connection import get_db
from infrastructure.repositories.event_repository import PostgreSQLEventRepository
from infrastructure.repositories.booking_repository import PostgreSQLBookingRepository
from infrastructure.repositories.ticket_repository import PostgreSQLTicketRepository

from presentation.api.schemas.event_schemas import (
    CreateEventRequest,
    CreateEventResponse,
    PublishEventRequest,
    PublishEventResponse,
    CancelEventRequest,
    CancelEventResponse,
    CreateTicketCategoryRequest,
    CreateTicketCategoryResponse,
    DisableTicketCategoryRequest,
    DisableTicketCategoryResponse,
    EventDetailResponse,
    EventListItemResponse,
    TicketCategoryResponse,
    ParticipantResponse,
    SalesReportResponse,
    CategorySalesResponse,
)

router = APIRouter(prefix="/events", tags=["Events"])


# ─────────────────────────────────────────────────────────
# Event CRUD
# ─────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=CreateEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new event",
)
def create_event(
    body: CreateEventRequest,
    db: Session = Depends(get_db),
) -> CreateEventResponse:
    """Event Organizer membuat event baru dengan status draft."""
    handler = CreateEventHandler(PostgreSQLEventRepository(db))
    command = CreateEventCommand(
        organizer_id=body.organizer_id,
        name=body.name,
        description=body.description,
        location=body.location,
        start_date=body.start_date,
        end_date=body.end_date,
        max_capacity=body.max_capacity,
    )
    try:
        result = handler.handle(command)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return CreateEventResponse(
        event_id=result.event_id,
        name=result.name,
        status=result.status,
    )


@router.get(
    "/",
    response_model=list[EventListItemResponse],
    summary="List all published events",
)
def list_events(db: Session = Depends(get_db)) -> list[EventListItemResponse]:
    """Menampilkan semua event yang sudah dipublish."""
    handler = GetAvailableEventsHandler(PostgreSQLEventRepository(db))
    query = GetAvailableEventsQuery()
    results = handler.handle(query)
    return [
        EventListItemResponse(
            event_id=r.event_id,
            name=r.name,
            location=r.location,
            start_date=r.start_date,
            end_date=r.end_date,
            lowest_price=r.lowest_price,
            currency=r.currency,
        )
        for r in results
    ]


@router.get(
    "/{event_id}",
    response_model=EventDetailResponse,
    summary="Get event detail",
)
def get_event_detail(
    event_id: UUID,
    db: Session = Depends(get_db),
) -> EventDetailResponse:
    """Menampilkan detail event beserta ticket categories yang aktif."""
    handler = GetEventDetailHandler(PostgreSQLEventRepository(db))
    query = GetEventDetailQuery(event_id=event_id)
    try:
        result = handler.handle(query)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    return EventDetailResponse(
        event_id=result.event_id,
        name=result.name,
        description=result.description,
        location=result.location,
        start_date=result.start_date,
        end_date=result.end_date,
        organizer_id=result.organizer_id,
        status=result.status,
        ticket_categories=[
            TicketCategoryResponse(
                category_id=tc.category_id,
                name=tc.name,
                price_amount=tc.price_amount,
                price_currency=tc.price_currency,
                quota=tc.quota,
                remaining_quota=tc.remaining_quota,
                sales_start=tc.sales_start,
                sales_end=tc.sales_end,
                availability_status=tc.availability_status,
            )
            for tc in result.ticket_categories
        ],
    )


@router.post(
    "/{event_id}/publish",
    response_model=PublishEventResponse,
    summary="Publish an event",
)
def publish_event(
    event_id: UUID,
    body: PublishEventRequest,
    db: Session = Depends(get_db),
) -> PublishEventResponse:
    """Event Organizer mempublish event agar bisa dibooking oleh customer."""
    handler = PublishEventHandler(PostgreSQLEventRepository(db))
    command = PublishEventCommand(event_id=event_id, organizer_id=body.organizer_id)
    try:
        result = handler.handle(command)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return PublishEventResponse(event_id=result.event_id, status=result.status)


@router.post(
    "/{event_id}/cancel",
    response_model=CancelEventResponse,
    summary="Cancel an event",
)
def cancel_event(
    event_id: UUID,
    body: CancelEventRequest,
    db: Session = Depends(get_db),
) -> CancelEventResponse:
    """Event Organizer membatalkan event."""
    handler = CancelEventHandler(PostgreSQLEventRepository(db))
    command = CancelEventCommand(event_id=event_id, organizer_id=body.organizer_id)
    try:
        result = handler.handle(command)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return CancelEventResponse(event_id=result.event_id, status=result.status)


# ─────────────────────────────────────────────────────────
# Ticket Category
# ─────────────────────────────────────────────────────────

@router.post(
    "/{event_id}/ticket-categories",
    response_model=CreateTicketCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a ticket category to an event",
)
def create_ticket_category(
    event_id: UUID,
    body: CreateTicketCategoryRequest,
    db: Session = Depends(get_db),
) -> CreateTicketCategoryResponse:
    """Event Organizer menambahkan kategori tiket ke event."""
    handler = CreateTicketCategoryHandler(PostgreSQLEventRepository(db))
    command = CreateTicketCategoryCommand(
        event_id=event_id,
        organizer_id=body.organizer_id,
        name=body.name,
        price_amount=body.price_amount,
        price_currency=body.price_currency,
        quota=body.quota,
        sales_start=body.sales_start,
        sales_end=body.sales_end,
    )
    try:
        result = handler.handle(command)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return CreateTicketCategoryResponse(
        category_id=result.category_id,
        name=result.name,
        quota=result.quota,
    )


@router.post(
    "/{event_id}/ticket-categories/{category_id}/disable",
    response_model=DisableTicketCategoryResponse,
    summary="Disable a ticket category",
)
def disable_ticket_category(
    event_id: UUID,
    category_id: UUID,
    body: DisableTicketCategoryRequest,
    db: Session = Depends(get_db),
) -> DisableTicketCategoryResponse:
    """Event Organizer menonaktifkan sebuah kategori tiket."""
    handler = DisableTicketCategoryHandler(PostgreSQLEventRepository(db))
    command = DisableTicketCategoryCommand(
        event_id=event_id,
        category_id=category_id,
        organizer_id=body.organizer_id,
    )
    try:
        result = handler.handle(command)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    return DisableTicketCategoryResponse(
        category_id=result.category_id,
        status=result.status,
    )


# ─────────────────────────────────────────────────────────
# Organizer Reports
# ─────────────────────────────────────────────────────────

@router.get(
    "/{event_id}/participants",
    response_model=list[ParticipantResponse],
    summary="Get list of participants for an event",
)
def get_participants(
    event_id: UUID,
    organizer_id: UUID,
    db: Session = Depends(get_db),
) -> list[ParticipantResponse]:
    """Event Organizer melihat daftar peserta yang sudah melakukan pembayaran."""
    event_repo = PostgreSQLEventRepository(db)
    booking_repo = PostgreSQLBookingRepository(db)
    ticket_repo = PostgreSQLTicketRepository(db)

    handler = GetParticipantsHandler(event_repo, booking_repo, ticket_repo)
    query = GetParticipantsQuery(event_id=event_id, organizer_id=organizer_id)
    try:
        results = handler.handle(query)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))

    return [
        ParticipantResponse(
            customer_id=p.customer_id,
            ticket_code=p.ticket_code,
            ticket_category_name=p.ticket_category_name,
            check_in_status=p.check_in_status,
        )
        for p in results
    ]


@router.get(
    "/{event_id}/sales-report",
    response_model=SalesReportResponse,
    summary="Get sales report for an event",
)
def get_sales_report(
    event_id: UUID,
    organizer_id: UUID,
    db: Session = Depends(get_db),
) -> SalesReportResponse:
    """Event Organizer melihat laporan penjualan tiket event."""
    event_repo = PostgreSQLEventRepository(db)
    booking_repo = PostgreSQLBookingRepository(db)

    handler = GetSalesReportHandler(event_repo, booking_repo)
    query = GetSalesReportQuery(event_id=event_id, organizer_id=organizer_id)
    try:
        result = handler.handle(query)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))

    return SalesReportResponse(
        event_id=result.event_id,
        event_name=result.event_name,
        total_revenue=result.total_revenue,
        currency=result.currency,
        booking_count_pending=result.booking_count_pending,
        booking_count_paid=result.booking_count_paid,
        booking_count_expired=result.booking_count_expired,
        booking_count_refunded=result.booking_count_refunded,
        categories=[
            CategorySalesResponse(
                category_id=c.category_id,
                name=c.name,
                quota=c.quota,
                sold=c.sold,
                remaining=c.remaining,
            )
            for c in result.categories
        ],
    )
