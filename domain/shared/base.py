from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


# ─ Base Domain Event
@dataclass(frozen=True)
class DomainEvent:
    """
    Base class for all domain events.
    frozen=True → immutable, cannot be modified after creation.
    Names are always past tense: EventCreated, BookingPaid, etc.
    """
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)


# ─ Base Entity
@dataclass(eq=False)
class Entity:
    """
    Base class for all entities.
    Entities have a unique identity (id) — two entities with the same id
    are considered the same object, even if other fields differ.
    eq=False → we define __eq__ ourselves based on id.
    """
    id: UUID = field(default_factory=uuid4)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


# ─ Base Aggregate Root
@dataclass(eq=False)
class AggregateRoot(Entity):
    """
    Base class for all aggregate roots.
    The aggregate root is the only entry point for modifying an aggregate.
    Holds a list of domain events raised during modification.
    """
    _domain_events: list = field(default_factory=list, init=False, repr=False)

    def _record_event(self, event: DomainEvent) -> None:
        """Record a domain event into the internal list."""
        self._domain_events.append(event)

    def pull_domain_events(self) -> list:
        """
        Return all recorded domain events and clear the internal list.
        Called by the Application Layer after the aggregate is persisted.
        """
        events = list(self._domain_events)
        self._domain_events.clear()
        return events