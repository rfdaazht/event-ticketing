from enum import Enum


class EventStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class TicketCategoryStatus(Enum):
    ACTIVE = "active"
    DISABLED = "disabled"