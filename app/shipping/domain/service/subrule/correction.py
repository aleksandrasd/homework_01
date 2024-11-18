from decimal import Decimal
from typing import Annotated

from pydantic import Field, validate_call

from app.shipping.domain.entity.transaction import UnprocessedTransaction
from app.shipping.domain.repository.transaction import TransactionRepo
from app.shipping.domain.service.subrule.base import BaseRuleSystem
from core.helper import get_calendar_month_range_dates


class CorrectionRule(BaseRuleSystem):
    """Correction rules that are responsible for ensuring accumulated discounts
    are not above predefined limit."""

    __rule_system__ = "correction"


class BasicMonthlyDiscountSizeLimiter(CorrectionRule):
    """
    Basic monthly discount size limiter.

    Ensures that monthly discount size is not above of threshold.
    If cumulative discount is above the threshold, discount is reduce to size
    that would make cumulative discount within allowed amount.

    Attributes:
      __rule_name__: unique rule name for rule registering
    """

    __rule_name__ = "basic_monthly_discount_size_limiter"

    @validate_call
    def __init__(self, size: Annotated[Decimal, Field(gt=0)]):
        """Initializes rule based on threshold size.

        Args:
            size: monthly discount size limit.
        """
        self._size = size

    async def correct(
        self,
        discount: Decimal,
        transaction: UnprocessedTransaction,
        transaction_repo: TransactionRepo,
    ) -> Decimal:
        """Correct discount

        Corrects discount: if sum of provided discount and accumulated monthly
        discounts is above monthly discount limit, then discount is reduce by
        amount that cumulative discount is above the threshold - this way
        ensuring that monthly discount is never above total monthly discount
        threshold.

        Args:
            discount: discount size.
            transaction: unprocessed transaction instance.
            transaction_repo: transaction repository.

        Returns:
            discount
        """
        start, end = get_calendar_month_range_dates(transaction.date)
        accumulated = await transaction_repo.get_discount_sum(
            start=start, end=end
        )
        if discount + accumulated <= self._size:
            return discount
        corrected_value = self._size - accumulated
        return corrected_value.max(0)
