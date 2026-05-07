from enum import Enum


class RefundStatus(Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID_OUT = "paid_out"