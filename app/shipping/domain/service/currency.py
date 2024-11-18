from core.helper.pydantic import make_decimal_places_formatter

CURRENCY_DECIMAL_PLACES = 2


def format_currency_decimal_places(x):
    return make_decimal_places_formatter(CURRENCY_DECIMAL_PLACES)(x)
