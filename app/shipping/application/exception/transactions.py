import datetime

from core.exceptions import CustomException


class InvalidTransactionRequestException(CustomException):
    """Transaction record is invalid."""

    message = "Transaction request validation failed"
    code = 422

    def __init__(self, message: str | None = None):
        if message is not None:
            self.message = message
        super().__init__(self.message)


class InvalidTransactionDateException(CustomException):
    """Transaction is outdated"""

    minimum_date: datetime.date
    code = 422

    def __init__(self, minimum_date: datetime.date):
        self.minimum_date = minimum_date

        if minimum_date.day > 1:
            date_str = minimum_date.strftime("%Y-%m-%d")
        elif minimum_date.month > 1:
            date_str = minimum_date.strftime("%Y-%m")
        else:
            date_str = minimum_date.strftime("%Y")

        self.message = f"Transactions older than {date_str} are not supported"
        super().__init__(self.message)
