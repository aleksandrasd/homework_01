from decimal import ROUND_DOWN, Decimal
from typing import Callable


def make_decimal_places_formatter(
    dec_places: int,
) -> Callable[[Decimal | None], Decimal | None]:
    """
    Provides function that enforces a specific number of decimal places on a
    Decimal value.

    Args:
        dec_places: the exact number of decimal places that the Decimal
                    value must have.

    Returns:
            A function that takes an Decimal or None and returns an Decimal
            or a None. The returned function ensures the Decimal value has
            exactly `dec_places` decimal places. If the value has more than
            `dec_places` decimal places and the extra places are not all zero,
            it raises a ValueError. Otherwise, it returns the value rounded
            down to exactly `dec_places` decimal places.

    Example:
        >>> from decimal import Decimal
        >>>
        >>> make_decimal_places_formatter(2)(Decimal('123.456'))
        Decimal('123.45')
        >>> make_decimal_places_formatter(2)(Decimal('123.4567'))
        ValueError: Value must have exactly 2 decimal places
        >>> make_decimal_places_formatter(2)(Decimal('123.40'))
        Decimal('123.40')
        >>> make_decimal_places_formatter(2)(Decimal('123.4000'))
        Decimal('123.40')
        >>> make_decimal_places_formatter(2)(None)
        None
    """

    def fun(value: Decimal | None) -> Decimal | None:
        if value is None:
            return None
        exponent = value.as_tuple().exponent
        if not isinstance(exponent, int):
            raise ValueError("Value must be a finite number.")
        
        got_dec_places = abs(exponent)
        if got_dec_places > dec_places:
            redundant_dec_place = value.as_tuple().digits[-dec_places:]
            if not all(dp == 0 for dp in redundant_dec_place):
                raise ValueError(
                    (f"Value must have exactly {dec_places}" " decimal places")
                )
        return value.quantize(
            Decimal(f'1.{"0"*dec_places}'), rounding=ROUND_DOWN
        )

    return fun
