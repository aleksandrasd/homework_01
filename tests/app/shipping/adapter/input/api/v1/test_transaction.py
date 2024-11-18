from datetime import datetime

import pytest

from app.shipping.application.exception.carrier import CarrierDisabledException
from app.shipping.application.exception.transactions import (
    InvalidTransactionDateException,
)


def test_rule(client):
    transactions = [
        {"date": "2022-01-01", "package_size": "S", "carrier": "A"},
        {"date": "2022-01-02", "package_size": "S", "carrier": "B"},
        {"date": "2022-01-03", "package_size": "XXL", "carrier": "A"},
        {"date": "2022-01-03", "package_size": "XS", "carrier": "A"},
        {"date": "2022-01-04", "package_size": "XXL", "carrier": "B"},
        {"date": "2022-01-05", "package_size": "S", "carrier": "A"},
        {"date": "2022-01-06", "package_size": "M", "carrier": "A"},
        {"date": "2022-01-07", "package_size": "M", "carrier": "B"},
        {"date": "2022-01-08", "package_size": "M", "carrier": "B"},
        {"date": "2022-01-09", "package_size": "M", "carrier": "A"},
        {"date": "2022-01-10", "package_size": "M", "carrier": "A"},
        {"date": "2022-01-12", "package_size": "L", "carrier": "B"},
        {"date": "2022-02-07", "package_size": "M", "carrier": "B"},
        {"date": "2022-02-08", "package_size": "M", "carrier": "B"},
        {"date": "2022-03-09", "package_size": "M", "carrier": "A"},
        {"date": "2022-03-09", "package_size": "L", "carrier": "A"},
        {"date": "2022-03-12", "package_size": "L", "carrier": "B"},
        {"date": "2022-04-14", "package_size": "M", "carrier": "A"},
    ]
    exp_resp = [
        {"reduced_price": "3", "applied_discount": None},
        {"reduced_price": "6.00", "applied_discount": None},
        {"reduced_price": "20.2", "applied_discount": "15.0"},
        {"reduced_price": "2", "applied_discount": None},
        {"reduced_price": "20.2", "applied_discount": None},
        {"reduced_price": "3", "applied_discount": None},
        {"reduced_price": "14.7", "applied_discount": None},
        {"reduced_price": "0.00", "applied_discount": "9.00"},
        {"reduced_price": "9.00", "applied_discount": None},
        {"reduced_price": "0.0", "applied_discount": "14.7"},
        {"reduced_price": "14.7", "applied_discount": None},
        {"reduced_price": "12.00", "applied_discount": None},
        {"reduced_price": "0.00", "applied_discount": "9.00"},
        {"reduced_price": "9.00", "applied_discount": None},
        {"reduced_price": "0.0", "applied_discount": "14.7"},
        {"reduced_price": "20.7", "applied_discount": None},
        {"reduced_price": "12.00", "applied_discount": None},
        {"reduced_price": "14.7", "applied_discount": None},
    ]

    got_resp = []
    got_status_codes = []
    for transaction in transactions:
        resp = client.post("/transactions", json=transaction)
        got_resp.append(resp.json())
        got_status_codes.append(resp.status_code)

    assert got_resp == exp_resp
    assert all(code == 200 for code in got_status_codes)


def test_date_validation(client):
    transactions = [
        {"date": "2001-01-01", "package_size": "XS", "carrier": "A"},
        {"date": "2001-02-01", "package_size": "XS", "carrier": "B"},
        {"date": "2001-02-16", "package_size": "M", "carrier": "A"},
    ]
    exc = InvalidTransactionDateException(datetime(2010, 1, 1))
    expected = []
    got = []
    for transaction in transactions:
        resp = client.post("/transactions", json=transaction)
        assert resp.status_code == exc.code
        assert exc.message in resp.text


def test_transaction_processing_in_conjunction_with_carrier_enable_status(
    client,
):
    request_groups = [
        {
            "set_enable_status": [{"code": "A", "enabled": False}],
            "expect_enable_statuses": {
                "carriers": [
                    {"code": "A", "enabled": False},
                    {"code": "B", "enabled": True},
                ]
            },
            "transaction": [
                {
                    "record": {
                        "date": "2015-02-01",
                        "package_size": "XS",
                        "carrier": "A",
                    },
                    "expect_exception": CarrierDisabledException("A"),
                },
                {
                    "record": {
                        "date": "2015-02-01",
                        "package_size": "XS",
                        "carrier": "B",
                    }
                },
            ],
        },
        {
            "set_enable_status": [
                {"code": "A", "enabled": True},
                {"code": "B", "enabled": False},
            ],
            "expect_enable_statuses": {
                "carriers": [
                    {"code": "A", "enabled": True},
                    {"code": "B", "enabled": False},
                ]
            },
            "transaction": [
                {
                    "record": {
                        "date": "2017-02-01",
                        "package_size": "XS",
                        "carrier": "B",
                    },
                    "expect_exception": CarrierDisabledException("B"),
                },
                {
                    "record": {
                        "date": "2018-02-01",
                        "package_size": "XS",
                        "carrier": "A",
                    }
                },
            ],
        },
    ]

    for rg in request_groups:
        for post in rg["set_enable_status"]:
            resp = client.post("/carriers", json=post)
            assert resp.status_code == 204
        resp = client.get("/carriers")
        assert resp.json() == rg["expect_enable_statuses"]

        for transaction_req in rg["transaction"]:
            resp = client.post(
                "/transactions",
                json=transaction_req["record"],
            )
            if "expect_exception" in transaction_req:
                assert resp.status_code == 422
                assert transaction_req["expect_exception"].message in resp.text
            else:
                assert resp.status_code == 200
