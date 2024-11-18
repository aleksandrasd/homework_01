from typing import TypedDict


class TransactionRequestDTO(TypedDict):
    """
    Transaction request contract.

    Attributes:
        date: the date of the transaction in ISO format.
        carrier: the carrier service name  used for the transaction
        package_size: the size of the package.
    """

    date: str
    carrier: str
    package_size: str
