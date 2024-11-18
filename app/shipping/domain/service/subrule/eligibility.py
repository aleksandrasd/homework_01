from typing import Annotated, Any

from pydantic import Field, validate_call

from app.shipping.domain.entity.transaction import UnprocessedTransaction
from app.shipping.domain.repository.transaction import TransactionRepo
from app.shipping.domain.service.subrule.base import BaseRuleSystem
from core.helper import attributes_equal, get_calendar_month_range_dates


class EligibilityRule(BaseRuleSystem):
    """Eligibility rules are responsible for determining transaction
    eligibility for the discount.
    """

    __rule_system__ = "eligibility"


class RuleTransactionAttributes(EligibilityRule):
    """Transaction attributes eligibility rule.

    Implements eligibility rule that transaction is eligible for discount if
    its attributes are equal to predefined values.

    Attributes:
      __rule_name__: unique rule name for rule registering
    """

    __rule_name__ = "rule_transaction_attributes"

    def __init__(self, **transaction):
        """Initializes transaction attributes rule based on rule's expected
        transaction attributes.

        Args:
          transaction: rule's expected attributes: attributes that transaction
                       would need to have in order to be eligible for a
                       discount.
        """
        self._transaction = transaction

    async def eligible(self, transaction: UnprocessedTransaction) -> bool:
        """Checks if transaction is eligible for the discount.

        Args:
            transaction: unprocessed transaction instance.

        Returns:
            true, if transaction is eligible for the discount.
        """
        return attributes_equal(transaction, **self._transaction)


class RuleMaxNTimesInCalendarMonth(EligibilityRule):
    """Eligibility rule that eligible for the discount no more than specified
    number of times in a calendar month.

    Attributes:
      __rule_name__: unique rule name for rule registering
    """

    __rule_name__ = "rule_max_n_times_in_calendar_month"

    @validate_call
    def __init__(self, discount_id: int, n: Annotated[int, Field(ge=1)]):
        """Initializes the rule instance based on discount id and number of
        time rule can be applied per calendar month.

        Args:
          discount_id: id of discount that rule is applicable for.
          n: number of times rule can be applied per month."""
        self._n = n
        self._discount_id = discount_id

    async def eligible(
        self,
        transaction: UnprocessedTransaction,
        transaction_repo: TransactionRepo,
    ) -> bool:
        """Checks if transaction is eligible for the discount.

        Args:
            transaction: unprocessed transaction instance.
            transaction_repo: transaction repository instance.

        Returns:
            true, if transaction is eligible for the discount.
        """
        start, end = get_calendar_month_range_dates(transaction.date)
        count = await transaction_repo.get_transaction_count(
            start=start,
            end=end,
            transaction_attr={"discount_id": self._discount_id},
        )
        return count < self._n


class RuleEveryNthTransaction(EligibilityRule):
    """Every n-th transaction is eligible for a discount

    Attributes:
      __rule_name__: unique rule name for rule registering.
    """

    __rule_name__ = "rule_every_nth_transaction"

    @validate_call
    def __init__(
        self,
        nth: Annotated[int, Field(ge=1)],
        transaction_attr: dict[str, Any] | None = None,
    ):
        """Initializes the rule based on interval and transaction attributes
        eligibility.

        Args:
            nth: transaction interval at which discount is set to be eligible
                 for a discount (e.g. nth = 2 means that every second
                 transaction is eligible for a discount).
            transaction_attr: transaction attribute that transaction
                              must have in order to be eligible for a discount.
        """
        self._nth = nth
        self._transaction_attr = (
            transaction_attr if transaction_attr is not None else {}
        )

    async def eligible(
        self,
        transaction: UnprocessedTransaction,
        transaction_repo: TransactionRepo,
    ) -> bool:
        """Checks if transaction is eligible for the discount.

        Args:
            transaction: unprocessed transaction instance.
            transaction_repo: transaction repository instance.

        Returns:
            true, if transaction is eligible for the discount.
        """
        if self._transaction_attr and not attributes_equal(
            transaction, **self._transaction_attr
        ):
            return False
        seq_num = await transaction_repo.get_transaction_count(
            transaction_attr=self._transaction_attr
        )
        current_nth = (
            seq_num + 1
        ) % self._nth  # +1 for including currently being
        # processed transaction.
        return current_nth == 0
