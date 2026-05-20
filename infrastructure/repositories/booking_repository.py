from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from domain.booking.aggregate import Booking
from domain.booking.value_objects import BookingStatus
from domain.shared.value_objects import Money
from domain.repositories.booking_repository import IBookingRepository
from infrastructure.database.models import BookingModel


class PostgreSQLBookingRepository(IBookingRepository):
    """Concrete implementation of IBookingRepository using PostgreSQL."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, booking: Booking) -> None:
        existing = self._db.query(BookingModel).filter_by(id=booking.id).first()
        if existing:
            self._update_model(existing, booking)
        else:
            self._db.add(self._to_model(booking))
        self._db.commit()

    def find_by_id(self, booking_id: UUID) -> Booking | None:
        model = self._db.query(BookingModel).filter_by(id=booking_id).first()
        return self._to_domain(model) if model else None

    def find_by_customer_and_event(
        self, customer_id: UUID, event_id: UUID
    ) -> Booking | None:
        """Return an active (pending_payment) booking for a customer+event pair."""
        model = (
            self._db.query(BookingModel)
            .filter_by(
                customer_id=customer_id,
                event_id=event_id,
                status="pending_payment",
            )
            .first()
        )
        return self._to_domain(model) if model else None

    def find_expired_pending(self) -> list[Booking]:
        """Return all pending bookings whose deadline has passed."""
        now = datetime.utcnow()
        models = (
            self._db.query(BookingModel)
            .filter(
                BookingModel.status == "pending_payment",
                BookingModel.payment_deadline < now,
            )
            .all()
        )
        return [self._to_domain(m) for m in models]

    def find_by_event(self, event_id: UUID) -> list[Booking]:
        models = self._db.query(BookingModel).filter_by(event_id=event_id).all()
        return [self._to_domain(m) for m in models]

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _to_model(self, booking: Booking) -> BookingModel:
        return BookingModel(
            id=booking.id,
            customer_id=booking.customer_id,
            event_id=booking.event_id,
            ticket_category_id=booking.ticket_category_id,
            quantity=booking.quantity,
            unit_price_amount=float(booking.unit_price.amount),
            unit_price_currency=booking.unit_price.currency,
            total_price_amount=float(booking.total_price.amount),
            total_price_currency=booking.total_price.currency,
            status=booking.status.value,
            payment_deadline=booking.payment_deadline,
            created_at=booking.created_at,
        )

    def _update_model(self, model: BookingModel, booking: Booking) -> None:
        model.status = booking.status.value

    def _to_domain(self, model: BookingModel) -> Booking:
        booking = Booking(
            id=model.id,
            customer_id=model.customer_id,
            event_id=model.event_id,
            ticket_category_id=model.ticket_category_id,
            quantity=model.quantity,
            unit_price=Money(
                Decimal(str(model.unit_price_amount)),
                model.unit_price_currency,
            ),
            total_price=Money(
                Decimal(str(model.total_price_amount)),
                model.total_price_currency,
            ),
            status=BookingStatus(model.status),
            payment_deadline=model.payment_deadline,
            created_at=model.created_at,
        )
        return booking