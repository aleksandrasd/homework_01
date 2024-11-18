from decimal import Decimal
from typing import Iterable

from app.shipping.domain.entity.shipping_plans import ShippingPlan
from app.shipping.domain.service.subrule.base import BaseRuleSystem
from core.helper import filter_objects


class SizeRule(BaseRuleSystem):
    """Size rule is responsible for determining discount size"""

    __rule_system__ = "size"


class RuleDiscountFullPrice(SizeRule):
    """Discount full price rule.

    Attributes:
      __rule_name__: unique rule name for rule registering.
    """

    __rule_name__ = "rule_discount_size_full_price"

    def __init__(self):
        pass

    async def calculate_discount(self, price: Decimal) -> Decimal:
        """Calculate discount

        Args:
            price: shipment service price

        Returns:
            discount
        """
        return price


class MatchPriceToLowestPriceAmongShippingPlans(SizeRule):
    """Match price to lowest price among shipping plans discount size rule

    Attributes:
      __rule_name__: unique rule name for rule registering.
    """

    __rule_name__ = "rule_match_price_to_lowest_among_shipping_plans"

    def __init__(self, attributes):
        """Initializes rule based on rules expected shipping plan attributes.

        Args:
          attributes: attributes of shipping plans that are applicable
                        for the rule.
        """
        self._attributes = attributes

    async def calculate_discount(
        self, price: Decimal, shipping_plans: Iterable[ShippingPlan]
    ) -> Decimal:
        """Calculate discount

        Args:
            price: shipment service price.
            shipping_plans: shipping plan iterable instances.
        Returns:
            discount
        """
        if self._attributes:
            shipping_plans = filter_objects(
                list(shipping_plans), **self._attributes
            )
        lowest_price = min(x.price for x in shipping_plans)
        return price - lowest_price
