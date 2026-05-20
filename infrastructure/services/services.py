"""
Infrastructure Layer — Application Service Implementations
Implementasi konkret dari interface service yang didefinisikan di application layer.
"""

import logging
import uuid
from decimal import Decimal
from uuid import UUID

from application.interfaces.notification_service import INotificationService
from application.interfaces.payment_gateway import IPaymentGatewayService, PaymentResult
from application.interfaces.refund_service import IRefundPaymentService, RefundResult

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────
# Payment Gateway — Implementasi Dummy/Stub
# ─────────────────────────────────────────────────────────

class DummyPaymentGatewayService(IPaymentGatewayService):
    """
    Implementasi stub dari IPaymentGatewayService.
    Digunakan untuk development dan testing — selalu mengembalikan sukses.

    Ganti dengan implementasi nyata (Midtrans, Xendit, dll.)
    saat aplikasi siap ke production.
    """

    def process_payment(
        self,
        booking_id: UUID,
        customer_id: UUID,
        amount: Decimal,
        currency: str,
    ) -> PaymentResult:
        """
        Simulasi proses pembayaran.
        Dalam production: kirim request ke payment gateway API.
        """
        transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"

        logger.info(
            "Payment processed | booking_id=%s | customer_id=%s | "
            "amount=%s %s | transaction_id=%s",
            booking_id,
            customer_id,
            amount,
            currency,
            transaction_id,
        )

        return PaymentResult(
            success=True,
            transaction_id=transaction_id,
            message="Payment successfully processed.",
        )


# ─────────────────────────────────────────────────────────
# Refund Payment Service — Implementasi Dummy/Stub
# ─────────────────────────────────────────────────────────

class DummyRefundPaymentService(IRefundPaymentService):
    """
    Implementasi stub dari IRefundPaymentService.
    Simulasi transfer refund ke rekening bank customer.

    Ganti dengan implementasi nyata (transfer bank, e-wallet, dll.)
    saat aplikasi siap ke production.
    """

    def process_refund(
        self,
        refund_id: UUID,
        customer_id: UUID,
        amount: Decimal,
        currency: str,
    ) -> RefundResult:
        """
        Simulasi proses disbursement refund ke rekening customer.
        Dalam production: kirim request ke bank/payment provider API.
        """
        payment_reference = f"REF-{uuid.uuid4().hex[:10].upper()}"

        logger.info(
            "Refund disbursed | refund_id=%s | customer_id=%s | "
            "amount=%s %s | payment_reference=%s",
            refund_id,
            customer_id,
            amount,
            currency,
            payment_reference,
        )

        return RefundResult(
            success=True,
            payment_reference=payment_reference,
            message="Refund successfully disbursed to customer account.",
        )


# ─────────────────────────────────────────────────────────
# Notification Service — Implementasi Dummy/Stub
# ─────────────────────────────────────────────────────────

class DummyNotificationService(INotificationService):
    """
    Implementasi stub dari INotificationService.
    Mencetak log ke console sebagai simulasi pengiriman notifikasi.

    Ganti dengan implementasi nyata (Email SMTP, WhatsApp API, Firebase, dll.)
    saat aplikasi siap ke production.
    """

    def send_booking_confirmation(
        self,
        customer_id: UUID,
        booking_id: UUID,
    ) -> None:
        """Kirim konfirmasi booking ke customer."""
        logger.info(
            "[NOTIF] Booking confirmation sent | customer_id=%s | booking_id=%s",
            customer_id,
            booking_id,
        )

    def send_payment_confirmation(
        self,
        customer_id: UUID,
        booking_id: UUID,
    ) -> None:
        """Kirim konfirmasi pembayaran berhasil ke customer."""
        logger.info(
            "[NOTIF] Payment confirmation sent | customer_id=%s | booking_id=%s",
            customer_id,
            booking_id,
        )

    def send_ticket_issued(
        self,
        customer_id: UUID,
        booking_id: UUID,
        ticket_codes: list[str],
    ) -> None:
        """Kirim kode tiket yang diterbitkan ke customer setelah pembayaran."""
        logger.info(
            "[NOTIF] Tickets issued | customer_id=%s | booking_id=%s | codes=%s",
            customer_id,
            booking_id,
            ticket_codes,
        )

    def send_refund_status(
        self,
        customer_id: UUID,
        refund_id: UUID,
        status: str,
    ) -> None:
        """Kirim notifikasi update status refund ke customer."""
        logger.info(
            "[NOTIF] Refund status update | customer_id=%s | refund_id=%s | status=%s",
            customer_id,
            refund_id,
            status,
        )

    def send_event_cancellation(
        self,
        customer_id: UUID,
        event_id: UUID,
    ) -> None:
        """Notifikasi ke customer bahwa event yang dibeli tiketnya dibatalkan."""
        logger.info(
            "[NOTIF] Event cancellation notice | customer_id=%s | event_id=%s",
            customer_id,
            event_id,
        )