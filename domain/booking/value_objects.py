from enum import Enum


class BookingStatus(Enum):
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    EXPIRED = "expired"
    REFUNDED = "refunded"