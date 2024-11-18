import asyncio
import datetime
import logging
from datetime import date
from decimal import Decimal
from typing import Iterable, List, TypedDict

from app.shipping.application.dto.request import TransactionRequestDTO
from app.shipping.application.dto.response import TransactionResponseDTO
from app.shipping.application.exception.carrier import (
    CarrierDisabledException,
    CarrierDoesNotExistsException,
)
from app.shipping.application.exception.transactions import (
    InvalidTransactionDateException,
    InvalidTransactionRequestException,
)
from app.shipping.domain.config import SUPPORT_TRANSACTION_DATE_START
from app.shipping.domain.entity.shipping_plans import ShippingPlan
from app.shipping.domain.entity.transaction import (
    ProcessedTransaction,
    UnprocessedTransaction,
)
from app.shipping.domain.repository.carrier import CarrierRepo
from app.shipping.domain.repository.discount_rules import DiscountRulesRepo
from app.shipping.domain.repository.transaction import TransactionRepo
from app.shipping.domain.service.discount import get_largest_discount
from app.shipping.domain.service.rule import DiscountRuleExecutor
from app.shipping.domain.service.subrule.correction import CorrectionRule
from app.shipping.domain.service.subrule.eligibility import EligibilityRule
from app.shipping.domain.service.subrule.size import SizeRule
from app.shipping.domain.uow import UnitOfWork
from app.shipping.domain.usecase.transaction import TransactionProcessorUseCase
from core.helper import filter_objects, find
from core.lock.base import BaseLock
from core.lock.exceptions import LockNotOwnedException

logger = logging.getLogger(__name__)


class _ApplicableDiscount(TypedDict):
    discount_id: int
    discount: Decimal


class TransactionProcessor(TransactionProcessorUseCase):
    """
    Transaction processor processes shipping transactions,
    including validating transaction requests, calculating shipping prices,
    applying discounts, and persisting the results.
    """

    def __init__(
        self,
        carrier_repo: CarrierRepo,
        discount_rules_repo: DiscountRulesRepo,
        transaction_repo: TransactionRepo,
        lock: BaseLock,
        uow: UnitOfWork,
        transaction_date_start: datetime.date = SUPPORT_TRANSACTION_DATE_START,
    ) -> None:
        """Initializes instance based on repositories, locking mechanism and
           transaction management mechanism.

        Args:
            carrier_repo: an instance of the carrier repository.
            discount_rules_repo: an instance of the discount rules repository.
            transaction_repo: transaction repository instance.
            lock:  a locking mechanism (`BaseLock` implementation), used for
                  concurrency control.
            uow: unit of work (`UnitOfWork` implementation), responsible for
                managing transactions.
            transaction_date_start: earliest date of transaction that
                                    the class supports.
        """
        self._transaction_repo = transaction_repo
        self._discount_rules_repo = discount_rules_repo
        self._carrier_repo = carrier_repo
        self._lock = lock
        self._uow = uow
        self._transaction_date_start = transaction_date_start

    async def _get_rules(self) -> List[DiscountRuleExecutor]:
        rules = []

        eligibility_rules = EligibilityRule.get_rules()
        size_rules = SizeRule.get_rules()
        correction_rules = CorrectionRule.get_rules()

        discount_rules = await self._discount_rules_repo.get_discount_rules()

        init_eligibility_rules = None
        init_correction_rule = None
        for discount_rule in discount_rules:
            if discount_rule.eligibility_rules is not None:
                init_eligibility_rules = [
                    eligibility_rules[rule.name](**rule.params)
                    for rule in discount_rule.eligibility_rules
                ]
            if discount_rule.size_correction_rule is not None:
                correction_rule = correction_rules[
                    discount_rule.size_correction_rule.name
                ]
                correction_params = discount_rule.size_correction_rule.params
                init_correction_rule = correction_rule(**correction_params)
            size_rule = size_rules[discount_rule.size_rule.name]
            size_params = discount_rule.size_rule.params
            rules.append(
                DiscountRuleExecutor(
                    discount_id=discount_rule.discount_id,
                    eligibility_rules=init_eligibility_rules,
                    size_rule=size_rule(**size_params),
                    size_correction_rule=init_correction_rule,
                )
            )
        return rules

    async def _validate_and_process_transaction_request(
        self,
        transaction: TransactionRequestDTO,
        shipping_plans: Iterable[ShippingPlan],
    ) -> UnprocessedTransaction:
        try:
            transaction_date = date.fromisoformat(transaction["date"])
        except ValueError:
            raise InvalidTransactionRequestException()

        try:
            transaction_obj = UnprocessedTransaction(
                date=transaction_date,
                package_size=transaction["package_size"],
                carrier=transaction["carrier"],
            )
        except ValueError:
            raise InvalidTransactionRequestException()

        is_enabled = await self._carrier_repo.is_enabled(
            transaction_obj.carrier
        )
        if is_enabled is None:
            raise CarrierDoesNotExistsException(transaction_obj.carrier)
        elif not is_enabled:
            raise CarrierDisabledException(transaction_obj.carrier)

        if transaction_date < self._transaction_date_start:
            raise InvalidTransactionDateException(self._transaction_date_start)

        carrier_plans = filter_objects(
            list(shipping_plans), carrier=transaction_obj.carrier
        )

        plan = filter_objects(
            carrier_plans, package_size=transaction_obj.package_size
        )

        if len(plan) == 0:
            raise InvalidTransactionRequestException(
                message=(
                    f"carrier {transaction_obj.carrier} does not provide"
                    f" service for package size {transaction_obj.package_size}"
                )
            )

        return transaction_obj

    def _get_price(
        self,
        transaction: UnprocessedTransaction,
        shipping_plans: Iterable[ShippingPlan],
    ) -> Decimal:
        shipping_plan = find(
            shipping_plans,
            carrier=transaction.carrier,
            package_size=transaction.package_size,
        )

        return shipping_plan.price

    def _get_response(
        self, price: Decimal, discount: Decimal | None
    ) -> TransactionResponseDTO:
        if discount is not None:
            reduced_price = price - discount
            applied_discount = discount
        else:
            reduced_price = price
            applied_discount = None

        return {
            "reduced_price": reduced_price,
            "applied_discount": applied_discount,
        }

    async def _calculate_discount(
        self,
        transaction: UnprocessedTransaction,
        shipping_plans: Iterable[ShippingPlan],
        price: Decimal,
        rules: Iterable[DiscountRuleExecutor],
    ) -> _ApplicableDiscount | None:
        exec_discount_tasks = []
        applicable_discounts: list[_ApplicableDiscount] = []
        async with asyncio.TaskGroup() as btg:
            for rule in rules:
                exec_rule_coro = rule.execute_rule(
                    transaction=transaction,
                    price=price,
                    shipping_plans=shipping_plans,
                    transaction_repo=self._transaction_repo,
                )
                exec_discount_tasks.append(
                    (rule.discount_id, btg.create_task(exec_rule_coro))
                )

        for discount_id, task in exec_discount_tasks:
            discount: Decimal | None = task.result()
            if discount is not None:
                applicable_discounts.append(
                    {"discount_id": discount_id, "discount": discount}
                )

        if len(applicable_discounts) == 0:
            return None
        return get_largest_discount(
            applicable_discounts, lambda x: x["discount"]
        )

    async def process_transaction(
        self, transaction: TransactionRequestDTO
    ) -> TransactionResponseDTO:
        """Process shipping transaction

        Processes shipping transactions, including calculating shipping prices,
        applying discounts, and persisting the results.

        Args:
            transaction: transaction request contract instance.

        Raises:
            CarrierDisabledException: if carrier service name in transaction
                                      record is currently disabled.
            InvalidTransactionRequestException: if transaction record is
                                                invalid.
            InvalidTransactionDateException: if transaction record's
                                             date is outside of supported
                                             transaction date ranges.

        Returns:
            transaction response contract instance.

        Note:
            Method calculates discount using predefined rules. The following
             class is responsible for executing discount rules:
            `app.shipping.domain.service.rule.DiscountRuleExecutor`.
        """
        shipping_plans = await self._carrier_repo.get_shipping_plans()
        unprocessed_transaction = (
            await self._validate_and_process_transaction_request(
                transaction, shipping_plans
            )
        )

        price = self._get_price(unprocessed_transaction, shipping_plans)
        rules = await self._get_rules()

        self._lock.acquire()

        try:
            async with self._uow:
                discount_size_and_id = await self._calculate_discount(
                    transaction=unprocessed_transaction,
                    shipping_plans=shipping_plans,
                    price=price,
                    rules=rules,
                )

                if discount_size_and_id is None:
                    applied_discount, applied_discount_id = None, None
                else:
                    applied_discount_id = discount_size_and_id["discount_id"]
                    applied_discount = discount_size_and_id["discount"]

                processed_transaction = ProcessedTransaction(
                    discount_id=applied_discount_id,
                    discount=applied_discount,
                    **transaction,  # type: ignore
                )

                await self._transaction_repo.save(processed_transaction)
                self._lock.reacquire()
        except Exception as e:
            try:
                self._lock.release()
            except LockNotOwnedException:
                pass
            raise e
        else:
            try:
                self._lock.release()
            except LockNotOwnedException:
                logger.warning(
                    (
                        "Failed to release lock after processing"
                        " transaction. This means that a race condition"
                        " may have occurred."
                    )
                )
        return self._get_response(price, applied_discount)
