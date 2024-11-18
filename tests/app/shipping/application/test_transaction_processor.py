from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest

from app.shipping.domain.entity.discount_rules import DiscountRule, Subrule
from core.lock.exceptions import LockNotOwnedException
from tests.support.container import get_mock_container
from tests.support.helper import get_applied_discount_bits, get_discounted_prices


@pytest.mark.asyncio
async def test_eligibility_rule_transaction_attributes(
    shipping_plan_set, carrier_statuses_set
):
    # GIVEN a rule that is applicable to transaction of package size S
    rules = [
        DiscountRule(
            discount_id=1,
            eligibility_rules=[
                Subrule(
                    name="rule_transaction_attributes",
                    params={"package_size": "S"},
                )
            ],
            size_rule=Subrule(
                name="rule_match_price_to_lowest_among_shipping_plans",
                params={"attributes": {"package_size": "S"}},
            ),
        ),
    ]

    mock_container = get_mock_container(
        shipping_plan_set, carrier_statuses_set, rules
    )

    # WHEN processing transactions
    transactions = [
        {"date": "2018-09-01", "package_size": "XS", "carrier": "A"},
        {"date": "2018-10-12", "package_size": "S", "carrier": "B"},
        {"date": "2018-11-12", "package_size": "M", "carrier": "B"},
    ]

    # THEN discount are applied only to transaction of package size S
    applied_discounts = await get_applied_discount_bits(
        mock_container, transactions
    )
    assert applied_discounts == [False, True, False]


@pytest.mark.asyncio
async def test_size_rule_match_price_to_lowest_among_shipping_plans(
    shipping_plan_set, carrier_statuses_set
):
    # GIVEN a rule that sets discount size equal to lowest among shipping plans
    rules = [
        DiscountRule(
            discount_id=1,
            size_rule=Subrule(
                name="rule_match_price_to_lowest_among_shipping_plans",
                params={"attributes": {"package_size": "S"}},
            ),
        ),
    ]

    mock_container = get_mock_container(
        shipping_plan_set, carrier_statuses_set, rules
    )

    # WHEN processing transactions
    transactions = [
        {"date": "2018-09-01", "package_size": "S", "carrier": "A"},
        {"date": "2018-10-12", "package_size": "S", "carrier": "B"},
    ]

    prices = await get_discounted_prices(mock_container, transactions)

    # THEN calculated discounts are limited
    expected_prices = [
        {"reduced_price": Decimal("3"), "applied_discount": None},
        {
            "reduced_price": Decimal("3.00"),
            "applied_discount": Decimal("3.00"),
        },
    ]
    assert prices == expected_prices


@pytest.mark.asyncio
async def test_basic_discount_limiter(shipping_plan_set, carrier_statuses_set):
    # GIVEN a rule that has a basic monthly discount size limiter
    rules = [
        DiscountRule(
            discount_id=1,
            size_rule=Subrule(name="rule_discount_size_full_price"),
            size_correction_rule=Subrule(
                name="basic_monthly_discount_size_limiter",
                params={"size": Decimal("25")},
            ),
        ),
    ]

    mock_container = get_mock_container(
        shipping_plan_set, carrier_statuses_set, rules
    )

    # WHEN processing transactions
    transactions = [
        {"date": "2018-09-01", "package_size": "XS", "carrier": "A"},
        {"date": "2018-09-10", "package_size": "S", "carrier": "A"},
        {"date": "2018-09-15", "package_size": "M", "carrier": "A"},
        {"date": "2018-12-12", "package_size": "S", "carrier": "B"},
    ]
    prices = await get_discounted_prices(mock_container, transactions)

    # THEN calculated discounts are limited
    expected_prices = [
        {"reduced_price": Decimal("0"), "applied_discount": Decimal("2")},
        {"reduced_price": Decimal("0"), "applied_discount": Decimal("3")},
        {"reduced_price": Decimal("0.0"), "applied_discount": Decimal("14.7")},
        {
            "reduced_price": Decimal("0.00"),
            "applied_discount": Decimal("6.00"),
        },
    ]
    assert prices == expected_prices


@pytest.mark.asyncio
async def test_multiple_eligibility_rules(
    shipping_plan_set, carrier_statuses_set
):
    # GIVEN a rule containing multiple eligibility subrules
    rules = [
        DiscountRule(
            discount_id=2,
            eligibility_rules=[
                Subrule(
                    name="rule_transaction_attributes",
                    params={"package_size": "XS"},
                ),
                Subrule(
                    name="rule_transaction_attributes", params={"carrier": "A"}
                ),
            ],
            size_rule=Subrule(name="rule_discount_size_full_price"),
        ),
    ]

    mock_container = get_mock_container(
        shipping_plan_set, carrier_statuses_set, rules
    )

    # WHEN processing transactions
    transactions = [
        {"date": "2018-09-01", "package_size": "XS", "carrier": "B"},
        {"date": "2018-10-12", "package_size": "M", "carrier": "A"},
        {"date": "2018-10-13", "package_size": "XS", "carrier": "A"},
    ]
    applied_discounts = await get_applied_discount_bits(
        mock_container, transactions
    )

    # THEN discount is applied for transactions only when all eligibility rules
    # allows it.
    assert applied_discounts == [False, False, True]


@pytest.mark.asyncio
async def test_rule_every_nth_transaction(
    shipping_plan_set, carrier_statuses_set
):
    # GIVEN a rule applicable to every second transaction for carrier A, size M
    rules = [
        DiscountRule(
            discount_id=1,
            eligibility_rules=[
                Subrule(
                    name="rule_every_nth_transaction",
                    params={
                        "nth": "2",
                        "transaction_attr": {
                            "carrier": "A",
                            "package_size": "M",
                        },
                    },
                )
            ],
            size_rule=Subrule(name="rule_discount_size_full_price"),
        )
    ]

    mock_container = get_mock_container(
        shipping_plan_set, carrier_statuses_set, rules
    )

    # WHEN processing transactions
    transactions = [
        {"date": "2018-09-01", "package_size": "M", "carrier": "A"},
        {"date": "2018-09-10", "package_size": "M", "carrier": "A"},
        {"date": "2018-09-10", "package_size": "M", "carrier": "B"},
        {"date": "2018-09-16", "package_size": "S", "carrier": "A"},
        {"date": "2018-09-24", "package_size": "XXL", "carrier": "B"},
    ]
    applied_discounts = await get_applied_discount_bits(
        mock_container, transactions
    )

    # THEN discount is applied for transactions only when rule is applicable
    assert applied_discounts == [False, True, False, False, False]


@pytest.mark.asyncio
async def test_rule_max_n_times_in_calendar_month(
    shipping_plan_set, carrier_statuses_set
):
    # GIVEN a rule applicable once a calendar month
    rules = [
        DiscountRule(
            discount_id=1,
            eligibility_rules=[
                Subrule(
                    name="rule_max_n_times_in_calendar_month",
                    params={"discount_id": "1", "n": "1"},
                )
            ],
            size_rule=Subrule(name="rule_discount_size_full_price"),
        ),
    ]

    mock_container = get_mock_container(
        shipping_plan_set, carrier_statuses_set, rules
    )

    # WHEN processing transactions
    transactions = [
        {"date": "2018-09-01", "package_size": "XS", "carrier": "A"},
        {"date": "2018-09-10", "package_size": "M", "carrier": "B"},
        {"date": "2018-10-16", "package_size": "S", "carrier": "A"},
        {"date": "2018-10-24", "package_size": "XXL", "carrier": "B"},
    ]
    applied_discounts = await get_applied_discount_bits(
        mock_container, transactions
    )

    # THEN discount is applied for transactions only when rule is applicable
    assert applied_discounts == [True, False, True, False]


@pytest.mark.asyncio
async def test_selects_biggest_discount_of_all_applicable_discounts(
    shipping_plan_set, carrier_statuses_set
):
    # GIVEN three discount rule applicable for every transaction, but provides
    # different discounts
    rules = [
        DiscountRule(
            discount_id=1,
            size_rule=Subrule(name="rule_discount_size_full_price"),
            size_correction_rule={
                "name": "basic_monthly_discount_size_limiter",
                "params": {"size": Decimal("0.1")},
            },
        ),
        DiscountRule(
            discount_id=2,
            size_rule=Subrule(name="rule_discount_size_full_price"),
            size_correction_rule={
                "name": "basic_monthly_discount_size_limiter",
                "params": {"size": Decimal("0.3")},
            },
        ),
        DiscountRule(
            discount_id=3,
            size_rule=Subrule(name="rule_discount_size_full_price"),
            size_correction_rule={
                "name": "basic_monthly_discount_size_limiter",
                "params": {"size": Decimal("0.2")},
            },
        ),
    ]

    mock_container = get_mock_container(
        shipping_plan_set, carrier_statuses_set, rules
    )

    # WHEN processing a transaction
    transactions = [
        {"date": "2015-02-01", "package_size": "S", "carrier": "A"}
    ]
    prices = await get_discounted_prices(mock_container, transactions)

    # THEN largest discount is applied
    assert prices[0]['applied_discount'] == Decimal('0.3')


@pytest.mark.asyncio
async def test_race_condition_occurrences_are_logged(
    any_valid_transaction, mock_container
):
    # GIVEN lock release method raises exception
    mock_container.lock.release.side_effect = LockNotOwnedException()
    processor = mock_container.get_transaction_processor_usecase()

    # WHEN processing any valid transaction
    with patch(
        "app.shipping.application.service.transaction.logger"
    ) as mock_logger:
        await processor.process_transaction(any_valid_transaction)

    # THEN logger outputs warning message containing keywords "race condition"
    assert mock_logger.warning.call_count > 0
    logged_warnings = [
        call[0][0] for call in mock_logger.warning.call_args_list
    ]
    assert any("race condition" in msg.lower() for msg in logged_warnings)


@pytest.mark.asyncio
async def test_unit_of_work_is_used_to_avoid_race_condition(
    any_valid_transaction, mock_container
):
    # GIVEN lock reacquire method raises exception
    mock_container.lock.reacquire.side_effect = LockNotOwnedException()
    processor = mock_container.get_transaction_processor_usecase()

    # WHEN processing any valid transaction
    with pytest.raises(LockNotOwnedException):
        await processor.process_transaction(any_valid_transaction)

    # THEN unit-of-work class methods "begin" and "abort" are called
    mock_container.uow.begin.assert_called()
    mock_container.uow.abort.assert_called()
