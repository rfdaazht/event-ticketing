"""
Presentation Layer — Ticket API Schemas
Pydantic models untuk request body dan response Ticket endpoints.
"""

from uuid import UUID

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────
# Request Schemas
# ─────────────────────────────────────────────────────────

class GetPurchasedTicketsRequest(BaseModel):
    customer_id: UUID


class CheckInTicketRequest(BaseModel):
    gate_officer_id: UUID
    ticket_code: str = Field(..., min_length=1)


# ─────────────────────────────────────────────────────────
# Response Schemas
# ─────────────────────────────────────────────────────────

class TicketResponse(BaseModel):
    ticket_id: UUID
    ticket_code: str
    event_id: UUID
    ticket_category_id: UUID
    status: str
    issued_at: str
    checked_in_at: str | None

    model_config = {"from_attributes": True}


class CheckInTicketResponse(BaseModel):
    ticket_id: UUID
    ticket_code: str
    status: str
    checked_in_at: str
