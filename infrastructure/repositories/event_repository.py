from uuid import UUID
from decimal import Decimal

from sqlalchemy.orm import Session

from domain.event.aggregate import Event, TicketCategory
from domain.event.value_objects import EventStatus, TicketCategoryStatus
from domain.shared.value_objects import Money
from domain.repositories.event_repository import IEventRepository
from infrastructure.database.models import EventModel, TicketCategoryModel


class PostgreSQLEventRepository(IEventRepository):
    """
    Concrete implementation of IEventRepository using PostgreSQL via SQLAlchemy.
    Handles mapping between domain aggregates and database models.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── Public Interface ──────────────────────────────────────────────────────

    def save(self, event: Event) -> None:
        """Save a new or updated Event aggregate to the database."""
        existing = self._db.query(EventModel).filter_by(id=event.id).first()
        if existing:
            self._update_model(existing, event)
        else:
            model = self._to_model(event)
            self._db.add(model)
        self._db.commit()

    def find_by_id(self, event_id: UUID) -> Event | None:
        """Return an Event aggregate by ID, or None if not found."""
        model = self._db.query(EventModel).filter_by(id=event_id).first()
        if model is None:
            return None
        return self._to_domain(model)

    def find_all_published(self) -> list[Event]:
        """Return all published events."""
        models = self._db.query(EventModel).filter_by(status="published").all()
        return [self._to_domain(m) for m in models]

    def find_by_organizer(self, organizer_id: UUID) -> list[Event]:
        """Return all events created by a specific organizer."""
        models = (
            self._db.query(EventModel)
            .filter_by(organizer_id=organizer_id)
            .all()
        )
        return [self._to_domain(m) for m in models]

    # ── Mapping Helpers ───────────────────────────────────────────────────────

    def _to_model(self, event: Event) -> EventModel:
        """Convert Event domain aggregate to EventModel ORM object."""
        model = EventModel(
            id=event.id,
            organizer_id=event.organizer_id,
            name=event.name,
            description=event.description,
            location=event.location,
            start_date=event.start_date,
            end_date=event.end_date,
            max_capacity=event.max_capacity,
            status=event.status.value,
        )
        for tc in event.ticket_categories:
            model.ticket_categories.append(self._to_category_model(tc))
        return model

    def _update_model(self, model: EventModel, event: Event) -> None:
        """Update an existing EventModel with values from Event aggregate."""
        model.name = event.name
        model.description = event.description
        model.location = event.location
        model.start_date = event.start_date
        model.end_date = event.end_date
        model.max_capacity = event.max_capacity
        model.status = event.status.value

        # Update or insert ticket categories
        existing_ids = {tc.id for tc in model.ticket_categories}
        for tc in event.ticket_categories:
            if tc.id in existing_ids:
                for m in model.ticket_categories:
                    if m.id == tc.id:
                        m.name = tc.name
                        m.price_amount = float(tc.price.amount)
                        m.price_currency = tc.price.currency
                        m.quota = tc.quota
                        m.sold = tc.sold
                        m.sales_start = tc.sales_start
                        m.sales_end = tc.sales_end
                        m.status = tc.status.value
            else:
                model.ticket_categories.append(self._to_category_model(tc))

    def _to_category_model(self, tc: TicketCategory) -> TicketCategoryModel:
        """Convert TicketCategory entity to TicketCategoryModel ORM object."""
        return TicketCategoryModel(
            id=tc.id,
            event_id=tc.event_id,
            name=tc.name,
            price_amount=float(tc.price.amount),
            price_currency=tc.price.currency,
            quota=tc.quota,
            sold=tc.sold,
            sales_start=tc.sales_start,
            sales_end=tc.sales_end,
            status=tc.status.value,
        )

    def _to_domain(self, model: EventModel) -> Event:
        """Convert EventModel ORM object back to Event domain aggregate."""
        event = Event(
            id=model.id,
            organizer_id=model.organizer_id,
            name=model.name,
            description=model.description or "",
            location=model.location,
            start_date=model.start_date,
            end_date=model.end_date,
            max_capacity=model.max_capacity,
            status=EventStatus(model.status),
        )
        for tc_model in model.ticket_categories:
            tc = TicketCategory(
                id=tc_model.id,
                event_id=tc_model.event_id,
                name=tc_model.name,
                price=Money(Decimal(str(tc_model.price_amount)), tc_model.price_currency),
                quota=tc_model.quota,
                sold=tc_model.sold,
                sales_start=tc_model.sales_start,
                sales_end=tc_model.sales_end,
                status=TicketCategoryStatus(tc_model.status),
            )
            event.ticket_categories.append(tc)
        return event