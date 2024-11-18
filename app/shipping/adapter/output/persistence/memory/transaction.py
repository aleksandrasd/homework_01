import datetime
from decimal import Decimal
from typing import Any

from app.shipping.domain.entity.transaction import ProcessedTransaction
from app.shipping.domain.repository.transaction import TransactionRepo
from core.helper import filter_objects


class TransactionMemoryRepo(TransactionRepo):
    """Transaction memory repository."""

    def __init__(self):
        self._transactions = []

    def _filter_transactions_by_date(
        self,
        transactions: list[ProcessedTransaction],
        start: datetime.date | None = None,
        end: datetime.date | None = None,
    ) -> list[ProcessedTransaction]:
        if start is not None:
            transactions = [t for t in transactions if start <= t.date]
        if end is not None:
            transactions = [t for t in transactions if t.date <= end]

        return transactions

    async def get_discount_sum(
        self,
        *,
        start: datetime.date | None = None,
        end: datetime.date | None = None,
        transaction_attr: dict[str, Any] | None = None,
    ) -> Decimal:
        """Calculates total sum of applied discounts.

        Args:
            start: if specified, starting date from when transactions with this
                   date or, later dates will be included in aggregation (
                   transactions with earlier date will not be included);
            end: if specified, last date that transactions will still be
                 included in aggregation (transactions with later date will
                 not be included);
            transaction_attr: if specified, only transaction with specified
                              attribute values will be included in calculation.

        Returns:
            Total sum of applied discounts.
        """
        transactions = self._transactions

        if transaction_attr:
            transactions = filter_objects(transactions, **transaction_attr)
        transactions = self._filter_transactions_by_date(
            transactions, start, end
        )
        total_elements = [
            t.discount for t in transactions if t.discount is not None
        ]
        if len(total_elements) == 0:
            return Decimal("0")
        return sum(total_elements)  # type: ignore

    async def get_transaction_count(
        self,
        *,
        start: datetime.date | None = None,
        end: datetime.date | None = None,
        transaction_attr: dict[str, Any] | None = None,
    ) -> int:
        """Get transaction count.

        Args:
            start: if specified, starting date from when transactions with this
                   date or, later dates will be included in aggregation (
                   transactions with earlier date will not be included);
            end: if specified, last date that transactions will still be
                 included in aggregation (transactions with later date will
                 not be included);
            transaction_attr: if specified, only transaction with specified
                              attribute values will be included in calculation.

        Returns:
            Transactions count.
        """
        transactions = self._transactions

        if transaction_attr:
            transactions = filter_objects(transactions, **transaction_attr)
        transactions = self._filter_transactions_by_date(
            transactions, start, end
        )

        return len(transactions)

    async def save(self, transaction: ProcessedTransaction) -> None:
        """Save processed transaction

        Arguments:
          transaction: process transaction instance
        """
        self._transactions.append(transaction)
