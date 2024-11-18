from decimal import Decimal

import pytest

from core.helper.pydantic import make_decimal_places_formatter


def test_make_decimal_places_formatter():
    two_decimals = make_decimal_places_formatter(2)
    assert two_decimals(Decimal("123.45")) == Decimal("123.45")
    with pytest.raises(ValueError):
        two_decimals(Decimal("123.4567"))
    assert two_decimals(Decimal("123.40")) == Decimal("123.40")
    assert two_decimals(Decimal("123.4000")) == Decimal("123.40")
    assert two_decimals(None) is None
