from dataclasses import dataclass
from typing import Iterable
from unittest import mock
from unittest.mock import AsyncMock

from app.container import Container, ContainerBase
from app.shipping.adapter.output.persistence.memory.carrier import CarrierMemoryRepo
from app.shipping.adapter.output.persistence.memory.transaction import (
    TransactionMemoryRepo,
)
from app.shipping.application.service.carrier import CarrierService
from app.shipping.application.service.transaction import TransactionProcessor
from app.shipping.domain.entity.carrier import CarrierEnableStatus
from app.shipping.domain.entity.shipping_plans import ShippingPlan
from app.shipping.domain.repository.discount_rules import DiscountRulesRepo
from app.shipping.domain.uow import UnitOfWork
from core.lock.base import BaseLock


def get_mock_container(
    shipping_plans: Iterable[ShippingPlan],
    carrier_statuses: Iterable[CarrierEnableStatus],
    rule_set,
) -> type[ContainerBase]:
    mock_discount_rule_repo = AsyncMock(spec=DiscountRulesRepo)
    mock_discount_rule_repo.get_discount_rules = AsyncMock(
        return_value=rule_set
    )
    carrier_memory_repo = CarrierMemoryRepo(shipping_plans, carrier_statuses)
    mock_lock = mock.create_autospec(BaseLock, instance=True)
    mock_uow = mock.create_autospec(UnitOfWork, instance=True)
    mock_uow.__aexit__ = UnitOfWork.__aexit__
    mock_uow.__aenter__ = UnitOfWork.__aenter__

    class MockContainer(Container):
        transaction_processor_usecase = TransactionProcessor
        carrier_manager_usecase = CarrierService
        transaction_repo = TransactionMemoryRepo()
        carrier_repo = carrier_memory_repo
        discount_rules_repo = mock_discount_rule_repo
        lock = mock_lock
        uow = mock_uow

    return MockContainer
