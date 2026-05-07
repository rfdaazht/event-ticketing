from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    """
    Value Object representing a monetary amount with its currency.

    frozen=True → immutable, cannot be modified after creation.
    Equality is based on value, not identity:
    Money(Decimal("10000"), "IDR") == Money(Decimal("10000"), "IDR") → True

    Rules:
    - Amount cannot be negative.
    - Currency must be a 3-character string (e.g. IDR, USD).
    """
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if self.amount < Decimal("0"):
            raise ValueError("Amount cannot be negative.")
        if len(self.currency) != 3:
            raise ValueError("Currency must be a 3-character code (e.g. IDR, USD).")

    def add(self, other: "Money") -> "Money":
        """Add two Money objects. Currency must match."""
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot add different currencies: {self.currency} and {other.currency}."
            )
        return Money(self.amount + other.amount, self.currency)

    def multiply(self, quantity: int) -> "Money":
        """Multiply amount by a quantity (e.g. ticket quantity)."""
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")
        return Money(self.amount * Decimal(quantity), self.currency)

    def is_equal_to(self, other: "Money") -> bool:
        """Check if two Money objects have the same amount and currency."""
        return self.amount == other.amount and self.currency == other.currency

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:,.2f}"