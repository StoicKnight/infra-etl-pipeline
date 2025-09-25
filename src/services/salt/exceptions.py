from typing import Optional


class SaltClientError(Exception):
    """Base exception for Salt API client errors."""

    pass


class SaltAPIError(SaltClientError):
    """
    Error occurred with the Salt API.

    Attributes:
        message (str): A description of the error.
        status_code (int | None): The HTTP status code of the response.
        response_text (str | None): The text content of the response.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_text = response_text

    def __str__(self):
        details = []
        if self.status_code:
            details.append(f"Status Code: {self.status_code}")
        if self.response_text:
            details.append(f"Response: {self.response_text[:200]}")

        if details:
            return f"{self.message} [{', '.join(details)}]"
        return self.message
