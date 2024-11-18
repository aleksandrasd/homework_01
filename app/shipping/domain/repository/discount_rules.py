from abc import ABC, abstractmethod

from app.shipping.domain.entity.discount_rules import DiscountRule


class DiscountRulesRepo(ABC):
    @abstractmethod
    async def get_discount_rules(self) -> list[DiscountRule]:
        """Get discount rules"""
