class VolStreetException(Exception):
    """Base class for other exceptions."""

    def __init__(self, message="VolStreet Exception", code=500):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ApiKeyNotFound(VolStreetException):
    """Exception raised for missing API Key in the environment variables."""

    def __init__(self, message="API Key not found", code=404):
        super().__init__(message, code)


class APIFetchError(VolStreetException):
    """Exception raised when unable to fetch data from Angel's API."""

    def __init__(self, message="No data returned from API", code=101):
        super().__init__(message, code)


class IntrinsicValueError(VolStreetException):
    """Exception raised when unable to calculate the greeks because of mismatch of intrinsic value and market price."""

    def __init__(
        self, message="Mismatch of intrinsic value and market price", code=3501
    ):
        super().__init__(message, code)


class ScripsLocationError(VolStreetException):
    """Exception raised when unable to locate something in the scrips file."""

    def __init__(
        self, message="Could not index scrips file", code=201, additional_info=""
    ):
        additional_info = (
            f"\nAdditional info: {additional_info}" if additional_info else ""
        )
        message = message + additional_info
        super().__init__(message, code)


class OptimizationError(VolStreetException):
    """Exception raised when unable to optimize the option positions."""

    def __init__(self, message, code=301):
        super().__init__(message, code)
