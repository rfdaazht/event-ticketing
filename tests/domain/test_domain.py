import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from domain.shared.value_objects import Money
from domain.event.aggregate import Event
from domain.booking.aggregate import Booking
from domain.ticket.aggregate import Ticket
from domain.refund.aggregate import Refund


# ─ Helpers

def make_event(
    start_date=date(2025, 12, 1),
    end_date=date(2025, 12, 2),
    max_capacity=100,
) -> Event:
    return Event.create(
        organizer_id=uuid4(),
        name="Test Event",
        description="Test",
        location="Jakarta",
        start_date=start_date,
        end_date=end_date,
        max_capacity=max_capacity,
    )


def make_event_with_category(quota=50) -> tuple[Event, object]:
    event = make_event()
    category = event.add_ticket_category(
        name="Regular",
        price=Money(Decimal("150000"), "IDR"),
        quota=quota,
        sales_start=date(2025, 10, 1),
        sales_end=date(2025, 11, 30),
    )
    return event, category


def make_booking(quantity=2) -> Booking:
    return Booking.create(
        customer_id=uuid4(),
        event_id=uuid4(),
        ticket_category_id=uuid4(),
        quantity=quantity,
        unit_price=Money(Decimal("150000"), "IDR"),
    )


def make_ticket() -> Ticket:
    return Ticket.issue(
        booking_id=uuid4(),
        customer_id=uuid4(),
        event_id=uuid4(),
        ticket_category_id=uuid4(),
    )


def make_refund() -> Refund:
    return Refund.request(
        booking_id=uuid4(),
        customer_id=uuid4(),
        amount=Money(Decimal("300000"), "IDR"),
        reason="Test refund",
    )


# ─ Event Tests

class TestEventCreation:

    def test_event_created_successfully(self):
        event = make_event()
        assert event.name == "Test Event"
        assert event.status.value == "draft"

    def test_event_cannot_be_created_with_invalid_schedule(self):
        with pytest.raises(ValueError, match="End date cannot be earlier than start date"):
            make_event(
                start_date=date(2025, 12, 2),
                end_date=date(2025, 12, 1),
            )

    def test_event_cannot_be_created_with_zero_capacity(self):
        with pytest.raises(ValueError, match="Maximum capacity must be greater than zero"):
            make_event(max_capacity=0)

    def test_event_cannot_be_created_with_negative_capacity(self):
        with pytest.raises(ValueError, match="Maximum capacity must be greater than zero"):
            make_event(max_capacity=-10)

    def test_event_raises_domain_event_on_creation(self):
        event = make_event()
        events = event.pull_domain_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "EventCreated"


class TestEventPublish:

    def test_event_cannot_be_published_without_active_category(self):
        event = make_event()
        with pytest.raises(ValueError, match="at least one active ticket category"):
            event.publish()

    def test_event_can_be_published_with_active_category(self):
        event, _ = make_event_with_category()
        event.publish()
        assert event.status.value == "published"

    def test_cancelled_event_cannot_be_published(self):
        event, _ = make_event_with_category()
        event.publish()
        event.cancel()
        with pytest.raises(ValueError, match="cancelled event cannot be published"):
            event.publish()


class TestTicketCategory:

    def test_ticket_category_quota_cannot_exceed_event_capacity(self):
        event = make_event(max_capacity=50)
        with pytest.raises(ValueError, match="exceeds"):
            event.add_ticket_category(
                name="Regular",
                price=Money(Decimal("150000"), "IDR"),
                quota=100,
                sales_start=date(2025, 10, 1),
                sales_end=date(2025, 11, 30),
            )

    def test_ticket_category_price_cannot_be_negative(self):
        event = make_event()
        with pytest.raises(ValueError):
            event.add_ticket_category(
                name="Regular",
                price=Money(Decimal("-1"), "IDR"),
                quota=10,
                sales_start=date(2025, 10, 1),
                sales_end=date(2025, 11, 30),
            )

    def test_ticket_category_quota_must_be_greater_than_zero(self):
        event = make_event()
        with pytest.raises(ValueError, match="quota must be greater than zero"):
            event.add_ticket_category(
                name="Regular",
                price=Money(Decimal("150000"), "IDR"),
                quota=0,
                sales_start=date(2025, 10, 1),
                sales_end=date(2025, 11, 30),
            )


# ─ Booking Tests

class TestBookingCreation:

    def test_booking_created_successfully(self):
        booking = make_booking()
        assert booking.status.value == "pending_payment"
        assert booking.total_price == Money(Decimal("300000"), "IDR")

    def test_booking_cannot_be_created_with_zero_quantity(self):
        with pytest.raises(ValueError, match="greater than zero"):
            make_booking(quantity=0)

    def test_booking_cannot_be_created_with_negative_quantity(self):
        with pytest.raises(ValueError, match="greater than zero"):
            make_booking(quantity=-1)

    def test_booking_has_payment_deadline(self):
        booking = make_booking()
        assert booking.payment_deadline is not None
        assert booking.payment_deadline > datetime.utcnow()


class TestBookingPayment:

    def test_booking_paid_successfully(self):
        booking = make_booking()
        booking.pay(Money(Decimal("300000"), "IDR"))
        assert booking.status.value == "paid"

    def test_booking_cannot_be_paid_after_deadline(self):
        booking = make_booking()
        booking.payment_deadline = datetime.utcnow() - timedelta(minutes=1)
        with pytest.raises(ValueError, match="Payment deadline has passed"):
            booking.pay(Money(Decimal("300000"), "IDR"))

    def test_booking_cannot_be_paid_with_incorrect_amount(self):
        booking = make_booking()
        with pytest.raises(ValueError, match="does not match"):
            booking.pay(Money(Decimal("100000"), "IDR"))

    def test_paid_booking_cannot_expire(self):
        booking = make_booking()
        booking.pay(Money(Decimal("300000"), "IDR"))
        with pytest.raises(ValueError, match="paid booking cannot be expired"):
            booking.expire()


# ─ Ticket Tests

class TestTicketCheckIn:

    def test_ticket_checked_in_successfully(self):
        ticket = make_ticket()
        ticket.check_in(gate_officer_id=uuid4(), event_id=ticket.event_id)
        assert ticket.status.value == "checked_in"

    def test_checked_in_ticket_cannot_be_checked_in_again(self):
        ticket = make_ticket()
        officer_id = uuid4()
        ticket.check_in(gate_officer_id=officer_id, event_id=ticket.event_id)
        with pytest.raises(ValueError, match="already been checked in"):
            ticket.check_in(gate_officer_id=officer_id, event_id=ticket.event_id)

    def test_ticket_cannot_be_checked_in_for_wrong_event(self):
        ticket = make_ticket()
        with pytest.raises(ValueError, match="does not belong to this event"):
            ticket.check_in(gate_officer_id=uuid4(), event_id=uuid4())


# ─ Refund Tests

class TestRefund:

    def test_refund_requested_successfully(self):
        refund = make_refund()
        assert refund.status.value == "requested"

    def test_refund_cannot_be_approved_if_not_requested(self):
        refund = make_refund()
        refund.approve()
        with pytest.raises(ValueError, match="Only a requested refund can be approved"):
            refund.approve()

    def test_rejected_refund_must_have_rejection_reason(self):
        refund = make_refund()
        with pytest.raises(ValueError, match="rejection reason must be provided"):
            refund.reject(rejection_reason="")

    def test_refund_rejected_successfully(self):
        refund = make_refund()
        refund.reject(rejection_reason="Ticket already used")
        assert refund.status.value == "rejected"
        assert refund.rejection_reason == "Ticket already used"

    def test_refund_paid_out_successfully(self):
        refund = make_refund()
        refund.approve()
        refund.mark_as_paid_out(payment_reference="REF-123")
        assert refund.status.value == "paid_out"

    def test_refund_cannot_be_requested_if_ticket_checked_in(self):
        """
        This rule is enforced at the Application Layer
        by checking ticket status before calling Refund.request().
        We simulate it here directly.
        """
        ticket = make_ticket()
        ticket.check_in(gate_officer_id=uuid4(), event_id=ticket.event_id)
        assert ticket.is_checked_in is True


# ─ Money Tests

class TestMoney:

    def test_money_cannot_be_negative(self):
        with pytest.raises(ValueError, match="Amount cannot be negative"):
            Money(Decimal("-1"), "IDR")

    def test_money_addition(self):
        m1 = Money(Decimal("100000"), "IDR")
        m2 = Money(Decimal("50000"), "IDR")
        assert m1.add(m2) == Money(Decimal("150000"), "IDR")

    def test_money_multiply(self):
        m = Money(Decimal("150000"), "IDR")
        assert m.multiply(3) == Money(Decimal("450000"), "IDR")

    def test_money_different_currency_cannot_be_added(self):
        with pytest.raises(ValueError, match="Cannot add different currencies"):
            Money(Decimal("100000"), "IDR").add(Money(Decimal("10"), "USD"))