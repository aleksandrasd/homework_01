from decimal import Decimal
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")


def get_largest_discount(
    discounts: Iterable[T], extract_size: Callable[[T], Decimal]
) -> T:
    return sorted(discounts, key=extract_size, reverse=True)[0]
