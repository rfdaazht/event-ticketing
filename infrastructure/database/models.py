from datetime import date, datetime
from uuid import UUID
import uuid

from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey,
    Integer, Numeric, String, Text, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database.connection import Base


# ─── Event ───────────────────────────────────────────────────────────────────

class EventModel(Base):
    __tablename__ = "events"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organizer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    max_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    ticket_categories: Mapped[list["TicketCategoryModel"]] = relationship(
        "TicketCategoryModel", back_populates="event", cascade="all, delete-orphan"
    )


class TicketCategoryModel(Base):
    __tablename__ = "ticket_categories"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    event_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("events.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    price_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    quota: Mapped[int] = mapped_column(Integer, nullable=False)
    sold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sales_start: Mapped[date] = mapped_column(Date, nullable=False)
    sales_end: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")

    event: Mapped["EventModel"] = relationship("EventModel", back_populates="ticket_categories")


# ─── Booking ──────────────────────────────────────────────────────────────────

class BookingModel(Base):
    __tablename__ = "bookings"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    customer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    event_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    ticket_category_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    unit_price_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    total_price_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    total_price_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending_payment"
    )
    payment_deadline: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )


# ─── Ticket ───────────────────────────────────────────────────────────────────

class TicketModel(Base):
    __tablename__ = "tickets"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    booking_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    event_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    ticket_category_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    ticket_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    issued_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    checked_in_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    checked_in_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=True)


# ─── Refund ───────────────────────────────────────────────────────────────────

class RefundModel(Base):
    __tablename__ = "refunds"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    booking_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="requested")
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[str] = mapped_column(Text, nullable=True)
    payment_reference: Mapped[str] = mapped_column(String(255), nullable=True)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    resolved_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)