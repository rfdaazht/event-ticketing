from dataclasses import dataclass
from uuid import UUID


# ─ Request DTOs

@dataclass
class CheckInTicketRequest:
    gate_officer_id: UUID
    ticket_code: str


# ─ Response DTOs

@dataclass
class TicketResponse:
    ticket_id: UUID
    ticket_code: str
    event_id: UUID
    ticket_category_id: UUID
    status: str
    issued_at: str
    checked_in_at: str | None


@dataclass
class CheckInTicketResponse:
    ticket_id: UUID
    ticket_code: str
    status: str
    checked_in_at: str