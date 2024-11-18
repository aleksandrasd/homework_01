import abc

from app.shipping.application.service.carrier import CarrierService
from app.shipping.application.service.transaction import TransactionProcessor
from app.shipping.domain.repository.carrier import CarrierRepo
from app.shipping.domain.repository.discount_rules import DiscountRulesRepo
from app.shipping.domain.repository.transaction import TransactionRepo
from app.shipping.domain.uow import UnitOfWork
from app.shipping.domain.usecase.carrier import CarrierUseCase
from app.shipping.domain.usecase.transaction import TransactionProcessorUseCase
from core.lock.base import BaseLock


class ContainerBase(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def get_transaction_processor_usecase(cls) -> TransactionProcessorUseCase:
        """Get transaction processor usecase"""

    @classmethod
    @abc.abstractmethod
    def get_carrier_manager_usecase(cls) -> CarrierUseCase:
        """Get carrier manager usecase"""


class Container(ContainerBase):
    transaction_processor_usecase: type[TransactionProcessor]
    carrier_manager_usecase: type[CarrierService]
    _transaction_processor_usecase: TransactionProcessor
    _carrier_manager_usecase: CarrierService
    carrier_repo: CarrierRepo
    transaction_repo: TransactionRepo
    discount_rules_repo: DiscountRulesRepo
    lock: BaseLock
    uow: UnitOfWork

    @classmethod
    def get_transaction_processor_usecase(cls) -> TransactionProcessorUseCase:
        if not hasattr(cls, "_transaction_processor_usecase"):
            cls._transaction_processor_usecase = (
                cls.transaction_processor_usecase(
                    carrier_repo=cls.carrier_repo,
                    discount_rules_repo=cls.discount_rules_repo,
                    transaction_repo=cls.transaction_repo,
                    lock=cls.lock,
                    uow=cls.uow,
                )
            )
        return cls._transaction_processor_usecase

    @classmethod
    def get_carrier_manager_usecase(cls) -> CarrierUseCase:
        if not hasattr(cls, "_carrier_manager_usecase"):
            cls._carrier_manager_usecase = cls.carrier_manager_usecase(
                carrier_repo=cls.carrier_repo
            )
        return cls._carrier_manager_usecase
