from abc import ABC, abstractmethod
from typing import Iterable

from app.shipping.domain.entity.carrier import CarrierEnableStatus


class CarrierUseCase(ABC):
    @abstractmethod
    async def set_enabled(self, carrier: str, *, enabled: bool) -> None:
        """Change carrier's enabled status"""

    @abstractmethod
    async def get_enable_statuses(self) -> Iterable[CarrierEnableStatus]:
        """Get carriers's enabled statuses"""
