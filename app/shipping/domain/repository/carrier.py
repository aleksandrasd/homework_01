from abc import ABC, abstractmethod
from typing import Iterable

from app.shipping.domain.entity.carrier import CarrierEnableStatus
from app.shipping.domain.entity.shipping_plans import ShippingPlan


class CarrierRepo(ABC):
    @abstractmethod
    async def set_enabled(self, carrier: str, enabled: bool) -> int:
        """Set carrier enabled"""

    @abstractmethod
    async def is_enabled(self, carrier: str) -> bool | None:
        """Check if carrier is enabled. Returns None if such carrier does not
        exist."""

    @abstractmethod
    async def get_enable_statuses(self) -> Iterable[CarrierEnableStatus]:
        """Get enable statuses"""

    @abstractmethod
    async def get_shipping_plans(self) -> Iterable[ShippingPlan]:
        """Get shipping plans"""
