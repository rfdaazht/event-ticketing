from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from domain.shared.value_objects import Money
from domain.repositories.booking_repository import IBookingRepository
from domain.repositories.ticket_repository import ITicketRepository
from domain.ticket.aggregate import Ticket
from application.interfaces.payment_gateway import IPaymentGatewayService
from application.interfaces.notification_service import INotificationService


@dataclass
class PayBookingCommand:
    """Command data for paying a booking."""
    booking_id: UUID
    customer_id: UUID
    amount_paid: Decimal
    currency: str


@dataclass
class PayBookingResult:
    """Result returned after successfully paying a booking."""
    booking_id: UUID
    status: str
    tickets_issued: int


class PayBookingHandler:
    """Handles the PayBooking command."""

    def __init__(
        self,
        booking_repository: IBookingRepository,
        ticket_repository: ITicketRepository,
        payment_gateway: IPaymentGatewayService,
        notification_service: INotificationService,
    ) -> None:
        self._booking_repository = booking_repository
        self._ticket_repository = ticket_repository
        self._payment_gateway = payment_gateway
        self._notification_service = notification_service

    def handle(self, command: PayBookingCommand) -> PayBookingResult:
        # Load booking
        booking = self._booking_repository.find_by_id(command.booking_id)
        if booking is None:
            raise ValueError(f"Booking {command.booking_id} not found.")
        if booking.customer_id != command.customer_id:
            raise ValueError("This booking does not belong to this customer.")

        # Process payment via external gateway
        payment_result = self._payment_gateway.process_payment(
            booking_id=booking.id,
            customer_id=booking.customer_id,
            amount=command.amount_paid,
            currency=command.currency,
        )
        if not payment_result.success:
            raise ValueError(f"Payment failed: {payment_result.message}")

        # Mark booking as paid — business rules enforced inside pay()
        amount_paid = Money(command.amount_paid, command.currency)
        booking.pay(amount_paid)
        self._booking_repository.save(booking)

        # Issue one ticket per quantity
        ticket_codes = []
        for _ in range(booking.quantity):
            ticket = Ticket.issue(
                booking_id=booking.id,
                customer_id=booking.customer_id,
                event_id=booking.event_id,
                ticket_category_id=booking.ticket_category_id,
            )
            self._ticket_repository.save(ticket)
            ticket_codes.append(ticket.ticket_code)

        # Send notifications
        self._notification_service.send_payment_confirmation(
            customer_id=booking.customer_id,
            booking_id=booking.id,
        )
        self._notification_service.send_ticket_issued(
            customer_id=booking.customer_id,
            booking_id=booking.id,
            ticket_codes=ticket_codes,
        )

        booking.pull_domain_events()

        return PayBookingResult(
            booking_id=booking.id,
            status=booking.status.value,
            tickets_issued=len(ticket_codes),
        )