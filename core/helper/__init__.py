import calendar
import copy
import datetime
import inspect
from typing import Any, Callable, Iterable, MutableSequence, TypeVar

T = TypeVar("T")
AnyMutableSequence = TypeVar("AnyMutableSequence", bound=MutableSequence)


def find(x: Iterable[T], **kwargs: Any) -> T:
    """Find an element in an iterable.

    Args:
      x: any iterable.
      **kwargs: search parameters: name is matched to object's attribute's name
              and value is matched to object's attribute's value.
    Returns:
      Returns first object in a sequence that meets search parameters.

    Raises:
      LookupError: if object is not found.
    """
    if len(kwargs) == 0:
        raise TypeError(
            "unable to find object since not a single "
            " search parameter was provided."
        )
    for element in x:
        found = True
        for search_name in kwargs:
            search_value = kwargs[search_name]
            if (
                not hasattr(element, search_name)
                or getattr(element, search_name) != search_value
            ):
                found = False
                break
        if found:
            return element

    text_params = ", ".join(
        f"{key}=={value!s}" for key, value in kwargs.items()
    )
    raise LookupError(
        (
            "unable to find element using provided search parameters:"
            f" {text_params}."
        )
    )


def filter_objects(
    x: AnyMutableSequence, **kwargs: Callable[[Any], bool] | Any
) -> AnyMutableSequence:
    """Get subset of sequence of objects that meets all conditions.

    Args:
        x: a sequence of objects.
        **kwargs: search parameters: name corresponds to sequence's object's
                attribute name and values are expected sequence's
                object's attribute value. If provided value is a callable
                then callable is called with passing object's attribute as an
                argument (callable is responsible for determining on whether
                attribute meets conditions)
    Returns:
        Returns shallow copy of provided mutable sequence with objects that
        contains attribute values equal to provided values or, in case of
        callables, returns objects whenever callables returned True for the 
        object.
    """
    y = copy.copy(x)
    if len(kwargs) == 0:
        raise TypeError(
            (
                "unable to filter the sequence since not a single"
                " search parameter was provided."
            )
        )
    for i, element in reversed(list(enumerate(x))):
        for search_name in kwargs:
            search_value = kwargs[search_name]
            value = getattr(element, search_name)
            if callable(search_value):
                if not search_value(value):
                    del y[i]
                    break
            elif value != search_value:
                del y[i]
                break

    return y


def attributes_equal(x: Any, **kwargs: Any) -> bool:
    """Checks if object's attributes have expected values

    Args:
        x: object
        **kwargs: names corresponds to object's attribute's names and
                  values are expected object's attribute's values.
    Raises:
        TypeError: if not a single pair of expected attribute name and value is
                   provided.
    Returns:
        bool: returns True if object attributes contains expected values.
              Otherwise, False is returned.
    """
    if len(kwargs) == 0:
        raise TypeError(
            (
                "unable to determine if object's attributes have expected"
                " values since not a single pair of attribute name and"
                " expected attribute value was passed."
            )
        )
    for search_name in kwargs:
        search_value = kwargs[search_name]
        if getattr(x, search_name) != search_value:
            return False
    return True


def call_with_expected_args(
    fun: Callable[..., T], ignore_self=True, /, **kwargs
) -> T:
    """Call callable with arguments that the callable is expecting.

    Reads provided callables expected arguments names. Then calls the callable
    with expected arguments names.

    Args:
        fun: callable that will be called with provided arguments.
        ignore_self: if first provided callable's argument is named 'self',
                     should we ignore this? Useful for class methods.
        kwargs: arguments for the callable. Must at least contain arguments
                needed for the provided callable (name must much callable's
                argument's name). Redundant arguments are ignored.

    Raises:
        TypeError: if not enough arguments supplied to call the provided
                  callable.

    Returns:
        Provided callable's output.
    """
    spec = inspect.getfullargspec(fun)

    if ignore_self and (len(spec.args) > 0 and spec.args[0] == "self"):
        kw = spec.args[1:] + spec.kwonlyargs
    else:
        kw = spec.args + spec.kwonlyargs

    missing_keys = set(kw) - set(kwargs.keys())
    if len(missing_keys) > 0:
        raise TypeError(f"Missing arguments: {', '.join(missing_keys)}.")

    args = dict((key, kwargs[key]) for key in kw)
    return fun(**args)


def has_method(obj: Any, name):
    return hasattr(obj, name) and callable(getattr(obj, name))


def has_arg(func, arg):
    sig = inspect.signature(func)
    return arg in sig.parameters


def has_method_arg(obj, method, arg):
    return has_arg(getattr(obj, method), arg)


def get_calendar_month_range_dates(date: datetime.date):
    """
    Returns the first and last date of the month for a given date.

    This function takes a date as input and returns a tuple containing the
    first day and the last day of the same month as the input date. It uses the
    `calendar.monthrange` function to determine the last day of the month.

    Args:
     date: a `datetime.date` object representing any date within the desired
           month.

    Example:
    >>> import datetime
    >>> date = datetime.date(2023, 10, 4)
    >>> get_calendar_month_range_dates(date)
    (datetime.date(2023, 10, 1), datetime.date(2023, 10, 31))
    """
    first_day_of_month = date.replace(day=1)
    _, last_day = calendar.monthrange(date.year, date.month)
    last_day_of_month = first_day_of_month.replace(day=last_day)
    return first_day_of_month, last_day_of_month
