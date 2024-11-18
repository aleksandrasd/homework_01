import datetime

from core.helper import (
    attributes_equal,
    call_with_expected_args,
    filter_objects,
    find,
    get_calendar_month_range_dates,
)
from tests.support.container import Person


def test_find_object_by_attribute():
    # given
    x = [
        Person(name="John", age=23),
        Person(name="Sandra", age=23),
        Person(name="Bob", age=36),
    ]

    # when
    y = find(x, name="Sandra")

    # then
    assert y == Person(name="Sandra", age=23)


def test_filter_objects_by_attributes():
    # given
    x = [
        Person(name="John", surname="ab", age=23),
        Person(name="Sandra", surname="dd", age=23),
        Person(name="Bob", surname="dd", age=44),
        Person(name="Alex", surname="dd", age=44),
        Person(name="Jim", surname="ll", age=44),
    ]

    # when
    got_objs = filter_objects(x, age=44, surname="dd")

    # then

    assert (
        got_objs[0] == Person(name="Bob", surname="dd", age=44)
        and got_objs[1] == Person(name="Alex", surname="dd", age=44)
        and len(got_objs) == 2
    )


def test_object_attributes_equal():
    assert attributes_equal(
        Person(name="John", surname="ab", age=23),
        name="John",
        surname="ab",
        age=23,
    )

    assert not attributes_equal(
        Person(name="John", surname="ab", age=23), name="John", age=66
    )


def test_call_with_expected_args():
    # Given
    class mock_class:
        def foo(self, a, b):
            return a, b

    def mock_foo(a, b):
        return a, b

    kwargs_1 = {"ze": 10, "b": 2, "a": 1, "gr": 56}
    kwargs_2 = {"ze": 10, "b": 200, "a": 10, "gr": 56}

    # when
    out_1 = call_with_expected_args(mock_foo, **kwargs_1)
    out_2 = call_with_expected_args(mock_class().foo, **kwargs_2)

    # then
    assert out_1 == (1, 2)
    assert out_2 == (10, 200)


def test_get_calendar_month_range_dates():
    # Given
    date = datetime.date(2023, 10, 4)

    # when
    out = get_calendar_month_range_dates(date)

    # then
    assert out == (datetime.date(2023, 10, 1), datetime.date(2023, 10, 31))
