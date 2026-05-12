from decimal import Decimal
from domain.shared.value_objects import Money


class PricingService:
    """
    Domain Service for calculating booking total price.
    Used when pricing logic involves more than one aggregate
    or requires external configuration (e.g. service fee).
    """

    SERVICE_FEE_PERCENTAGE = Decimal("0.05")  # 5% service fee

    @staticmethod
    def calculate_total(unit_price: Money, quantity: int) -> Money:
        """
        Calculate total booking price including service fee.
        total = (unit_price * quantity) + service_fee
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        subtotal = unit_price.multiply(quantity)
        service_fee = Money(
            amount=(subtotal.amount * PricingService.SERVICE_FEE_PERCENTAGE),
            currency=subtotal.currency,
        )
        return subtotal.add(service_fee)