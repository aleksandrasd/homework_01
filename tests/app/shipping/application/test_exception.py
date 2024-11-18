from datetime import date

import pytest

from app.shipping.application.exception.transactions import (
    InvalidTransactionDateException,
)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (date(2010, 1, 1), "Transactions older than 2010 are not supported"),
        (
            date(2010, 2, 1),
            "Transactions older than 2010-02 are not supported",
        ),
        (
            date(2010, 2, 15),
            "Transactions older than 2010-02-15 are not supported",
        ),
    ],
)
def test_invalid_transaction_date_exception(test_input, expected):
    assert InvalidTransactionDateException(test_input).message == expected
