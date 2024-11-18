import datetime
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any

from app.shipping.domain.entity.transaction import ProcessedTransaction


class TransactionRepo(ABC):
    @abstractmethod
    async def get_transaction_count(
        self,
        *,
        start: datetime.date | None = None,
        end: datetime.date | None = None,
        transaction_attr: dict[str, Any],
    ) -> int:
        """Get transaction count"""

    @abstractmethod
    async def get_discount_sum(
        self,
        *,
        start: datetime.date | None = None,
        end: datetime.date | None = None,
        transaction_attr: dict[str, Any] | None = None,
    ) -> Decimal:
        """Get the sum of applied discounts."""

    @abstractmethod
    async def save(self, transaction: ProcessedTransaction) -> None:
        """Store transaction"""
