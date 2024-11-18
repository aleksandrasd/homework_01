from decimal import Decimal
from typing import Iterable

from fastapi.testclient import TestClient
from pytest import fixture

from app.container import Container
from app.server import build_app
from app.shipping.domain.entity.carrier import CarrierEnableStatus
from app.shipping.domain.entity.discount_rules import DiscountRule, Subrule
from app.shipping.domain.entity.shipping_plans import ShippingPlan
from tests.support.container import get_mock_container


@fixture
def shipping_plan_set() -> Iterable[ShippingPlan]:
    return [
        ShippingPlan(carrier="A", package_size="XS", price=Decimal("2")),
        ShippingPlan(carrier="A", package_size="S", price=Decimal("3")),
        ShippingPlan(carrier="A", package_size="M", price=Decimal("14.7")),
        ShippingPlan(carrier="A", package_size="L", price=Decimal("20.7")),
        ShippingPlan(carrier="A", package_size="XL", price=Decimal("28.8")),
        ShippingPlan(carrier="A", package_size="XXL", price=Decimal("35.2")),
        ShippingPlan(carrier="B", package_size="XS", price=Decimal("3.5")),
        ShippingPlan(carrier="B", package_size="S", price=Decimal("6.00")),
        ShippingPlan(carrier="B", package_size="M", price=Decimal("9.00")),
        ShippingPlan(carrier="B", package_size="L", price=Decimal("12.00")),
        ShippingPlan(carrier="B", package_size="XL", price=Decimal("40.8")),
        ShippingPlan(carrier="B", package_size="XXL", price=Decimal("20.2")),
    ]


@fixture
def carrier_statuses_set() -> Iterable[CarrierEnableStatus]:
    return [
        CarrierEnableStatus(carrier="A", enabled=True),
        CarrierEnableStatus(carrier="B", enabled=True),
    ]


@fixture
def rule_set() -> Iterable[DiscountRule]:
    return [
        DiscountRule(
            discount_id=1,
            eligibility_rules=[
                Subrule(
                    name="rule_transaction_attributes",
                    params={"package_size": "XXL"},
                )
            ],
            size_rule=Subrule(
                name="rule_match_price_to_lowest_among_shipping_plans",
                params={"attributes": {"package_size": "XXL"}},
            ),
        ),
        DiscountRule(
            discount_id=2,
            eligibility_rules=[
                Subrule(
                    name="rule_max_n_times_in_calendar_month",
                    params={"discount_id": "4", "n": "1"},
                ),
                Subrule(
                    name="rule_every_nth_transaction",
                    params={
                        "nth": "2",
                        "transaction_attr": {"package_size": "M"},
                    },
                ),
            ],
            size_rule=Subrule(name="rule_discount_size_full_price"),
            size_correction_rule=Subrule(
                name="basic_monthly_discount_size_limiter",
                params={"size": Decimal("40")},
            ),
        ),
    ]


@fixture
def any_valid_transaction():
    return {"date": "2021-02-01", "package_size": "S", "carrier": "A"}


@fixture
def any_valid_s_package_size_transaction():
    return {"date": "2021-02-01", "package_size": "S", "carrier": "A"}


@fixture
def mock_container(shipping_plan_set, carrier_statuses_set, rule_set):
    return get_mock_container(
        shipping_plan_set, carrier_statuses_set, rule_set
    )


@fixture
def client(mock_container):
    app = build_app()
    app.dependency_overrides[Container.get_carrier_manager_usecase] = (
        mock_container.get_carrier_manager_usecase
    )
    app.dependency_overrides[Container.get_transaction_processor_usecase] = (
        mock_container.get_transaction_processor_usecase
    )
    return TestClient(app)
