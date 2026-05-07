from enum import Enum


class TicketStatus(Enum):
    ACTIVE = "active"
    CHECKED_IN = "checked_in"
    CANCELLED = "cancelled"