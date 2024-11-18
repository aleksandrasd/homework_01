from typing import Iterable

from app.shipping.domain.entity.carrier import CarrierEnableStatus
from app.shipping.domain.entity.shipping_plans import ShippingPlan
from app.shipping.domain.repository.carrier import CarrierRepo
from core.helper import filter_objects


class CarrierMemoryRepo(CarrierRepo):
    """Carrier in memory repository."""

    def __init__(
        self,
        shipping_plans: Iterable[ShippingPlan],
        carrier_statuses: Iterable[CarrierEnableStatus],
    ) -> None:
        """
        Initializes carrier memory repository based on provided shipping plans
        and default carrier statuses.

        Arguments:
          shipping_plans: iterable of shipping plan instances.
          carrier_statuses: iterable of carrier enable status instances.
        """
        self._shipping_plans = list(shipping_plans)
        self._carrier_statuses = list(carrier_statuses)

    async def get_shipping_plans(self) -> Iterable[ShippingPlan]:
        """Get shipping plans

        Returns:
            iterable of shipping plan instances.
        """
        enabled_shipping_plans = []
        for status in self._carrier_statuses:
            if status.enabled:
                enabled_shipping_plans.extend(
                    filter_objects(
                        self._shipping_plans, carrier=status.carrier
                    )
                )

        return enabled_shipping_plans

    async def set_enabled(self, carrier: str, enabled: bool) -> int:
        """Set enable status of a carrier

        Args:
            carrier: carrier service name;
            enabled: enabled status: set true to enable carrier, set false to
                     disable carrier.

        Returns:
            number of affected carriers
        """
        statuses = filter_objects(self._carrier_statuses, carrier=carrier)
        for status in statuses:
            status.enabled = enabled
        return len(statuses)

    async def is_enabled(self, carrier: str) -> bool | None:
        """Check if carrier is enabled

        Args:
            carrier: carrier service name

        Returns:
            if carrier is enabled, true is returned. Otherwise, false is
            returned.
        """
        statuses = filter_objects(self._carrier_statuses, carrier=carrier)
        if len(statuses) == 0:
            return None
        return statuses[0].enabled

    async def get_enable_statuses(self) -> Iterable[CarrierEnableStatus]:
        """Get enable status of every carrier

        Returns:
            iterable of carrier enable status instances.
        """
        return self._carrier_statuses
