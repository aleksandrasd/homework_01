from core.exceptions import CustomException


class CarrierDisabledException(CustomException):
    """Carrier is disabled"""

    code = 422

    def __init__(self, carrier: str):
        self.message = f"Carrier with code '{carrier}' is disabled"
        super().__init__(self.message)


class CarrierDoesNotExistsException(CustomException):
    """Such carrier does not exists."""

    code = 422

    def __init__(self, carrier: str):
        self.message = f"Carrier with code '{carrier}' does not exist"
        super().__init__(self.message)
