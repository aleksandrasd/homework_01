"""Execute rules.

Contains domain logic for executing rules.

Design Notes:
  Subrules do not need to implement any abstract class. Subrule required
  parameters determined during runtime.

  Approach's advantages over polymorphism:
    * readability: subrules has only method arguments they actually use (
                  abstract classes would required to declare parameters
                  even if subrules do not require them);
    * maintainability: if subrule requires additional argument, you don't
                       need to modify existing rules's method definitions
                       to include the new argument (like you would need in
                       case of polymorphism).
  Approach's disadvantages:
    * linter would not be able to detect when not all required method
      arguments are provided or when not correct type arguments are provided
      ahead of runtime.
"""

import asyncio
import logging
from decimal import Decimal
from typing import Any, Iterable, Mapping

from app.shipping.domain.entity.shipping_plans import ShippingPlan
from app.shipping.domain.entity.transaction import UnprocessedTransaction
from app.shipping.domain.repository.transaction import TransactionRepo
from core.helper import call_with_expected_args, has_method, has_method_arg

logger = logging.getLogger(__name__)


class DiscountRuleExecutor:
    """Executes discount rule.

    Executes discount rules by executing rule's subrules
    """

    def __init__(
        self,
        *,
        discount_id: int,
        size_rule: object,
        eligibility_rules: Iterable[object] | None = None,
        size_correction_rule: object | None = None,
    ):
        """Initializes rule instance based on provided subrules.

        Args:
            discount_id: unique discount identifier.
            size_rule: size rule object that has a method `calculate_discount`
                       for calculating discount size.
            eligibility_rules: eligibility rule objects that have a method
                               `eligible` for determining whether
                               transaction is eligible for discount.
            size_correction_rule: size correction object that has a method
                                 `correct` for correcting discount size.

        Raises:
            ValueError: in the following situations:
                  * `size_rule` does not have callable `calculate_discount`;
                  * any of `eligibility_rules` that does not have callable
                    `eligible`;
                  * `size_rule` does not have callable `correct`;

        Notes:
            Rules(subrules) do not need to implement any abstract class.
            Method's arguments are determined individually for each rule and
            based on that determination inputs are provided for the method.
        """

        if eligibility_rules:
            for eligibility_rule in eligibility_rules:
                if not has_method(eligibility_rule, "eligible"):
                    raise ValueError(
                        (
                            "Eligibility class must have a callable method"
                            " 'eligible'."
                        )
                    )

        if not has_method(size_rule, "calculate_discount"):
            raise ValueError(
                (
                    "Size rule class must have a callable method",
                    " 'calculate_discount'.",
                )
            )

        if size_correction_rule is not None:
            if not has_method(size_correction_rule, "correct"):
                raise ValueError(
                    (
                        "Size correction class must have a callable method"
                        " 'correct'."
                    )
                )

            if not has_method_arg(size_correction_rule, "correct", "discount"):
                raise ValueError(
                    (
                        "Size correction class method 'correct' must have"
                        " argument 'discount'."
                    )
                )

        self.discount_id = discount_id

        self._eligibility_rules = eligibility_rules
        self._size_rule = size_rule
        self._size_correction_rule = size_correction_rule

    async def execute_rule(
        self,
        price: Decimal,
        shipping_plans: Iterable[ShippingPlan],
        transaction: UnprocessedTransaction,
        transaction_repo: TransactionRepo,
        rule_params: dict[str, Any] | None = None,
    ) -> Decimal | None:
        """Executes rule.

          Executes rule by executing subrules. Arguments are hand over
          to subrules.

        Args:
            price: shipping price
            shipping_plans: iterable containing shipping plan instances.
            transaction: instance of unprocessed transaction instance.
            transaction_repo: transaction repository instance.
            rule_params: additional parameters for subrules.

        Returns:
            Returns discount size if discount rule is applicable. Otherwise,
            returns None.

        """
        if rule_params:
            rule_params = rule_params.copy()
        else:
            rule_params = {}

        rule_params["transaction"] = transaction
        rule_params["price"] = price
        rule_params["shipping_plans"] = shipping_plans
        rule_params["transaction_repo"] = transaction_repo

        is_eligible = await self._is_eligible(
            self._eligibility_rules, rule_params
        )

        if not is_eligible:
            return None

        size = await call_with_expected_args(
            self._size_rule.calculate_discount,  # type: ignore
            True,
            **rule_params,
        )

        if size < 0:
            logger.error(
                (
                    "Discount calculation subrule returned negative discount."
                    " Returning that no discount is applicable."
                )
            )
            return None

        if self._size_correction_rule is None:
            return None if size == 0 else size

        rule_params_with_discount = rule_params.copy()
        rule_params_with_discount["discount"] = size
        corrected_size = await call_with_expected_args(
            self._size_correction_rule.correct,  # type: ignore
            True,
            **rule_params_with_discount,
        )

        if corrected_size is not None and corrected_size < 0:
            logger.error(
                (
                    "Discount correction subrule returned negative discount."
                    " Returning that no discount is applicable."
                )
            )
            return None

        return None if corrected_size == 0 else corrected_size

    async def _is_eligible(
        self,
        eligibility_rules: Iterable[object] | None,
        rule_params: Mapping[str, Any],
    ) -> bool:
        if eligibility_rules is None:
            return True

        eligibility_tasks = []
        for i, rule in enumerate(eligibility_rules):
            eligible = call_with_expected_args(
                rule.eligible, True, **rule_params  # type: ignore
            )
            task = asyncio.create_task(eligible, name=f"eligibility rule: {i}")
            eligibility_tasks.append(task)

        for eligibility_coroutine in asyncio.as_completed(eligibility_tasks):
            is_eligible = await eligibility_coroutine
            if not is_eligible:
                for task in eligibility_tasks:
                    task.cancel()
                return False
        return True
