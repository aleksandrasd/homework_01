from decimal import Decimal
from typing import TypedDict


class TransactionResponseDTO(TypedDict):
    """
    Transaction response contract.

    Attributes:
      reduced_price: the final price of the transaction after applying
                      discounts.
      applied_discount: the amount of discount applied to the transaction.
    """

    reduced_price: Decimal
    applied_discount: Decimal | None
