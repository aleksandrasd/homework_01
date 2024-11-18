from typing import Iterable

from app.shipping.application.exception.carrier import (
    CarrierDoesNotExistsException,
)
from app.shipping.domain.entity.carrier import CarrierEnableStatus
from app.shipping.domain.repository.carrier import CarrierRepo
from app.shipping.domain.usecase.carrier import CarrierUseCase


class CarrierService(CarrierUseCase):

    def __init__(self, carrier_repo: CarrierRepo) -> None:
        """
        Initializes instance based on carrier repository selection.

        Args:
          carrier_repo: carrier repository instance.
        """
        self._carrier_repo = carrier_repo

    async def set_enabled(self, carrier: str, *, enabled: bool) -> None:
        """
        Enables or disables a carrier.

        Args:
          carrier: the name or identifier of the carrier to be updated.

          enabled: a flag indicating whether the carrier should be enabled (
                  True) or disabled (False).

        Raises:
          CarrierDoesNotExistsException:
              If the specified carrier does not exist in the repository, the
              exception is raised.
        """
        res = await self._carrier_repo.set_enabled(carrier, enabled)
        if res == 0:
            raise CarrierDoesNotExistsException(carrier=carrier)

    async def get_enable_statuses(self) -> Iterable[CarrierEnableStatus]:
        return await self._carrier_repo.get_enable_statuses()
