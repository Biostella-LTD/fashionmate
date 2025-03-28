from typing import Any, Dict


class HTTPError(Exception):
    """Base class for HTTP errors"""

    def __init__(self, status_code: int, error: str, message: str):
        self.status_code = status_code
        self.error = error
        self.message = message
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON response"""
        return {
            "status_code": self.status_code,
            "error": self.error,
            "message": self.message,
        }


class BadRequestError(HTTPError):
    """400 Bad Request error"""

    def __init__(self, error: str, message: str):
        super().__init__(400, error, message)


class NotFoundError(HTTPError):
    """404 Not Found error"""

    def __init__(self, error: str, message: str):
        super().__init__(404, error, message)


class ValidationError(HTTPError):
    """422 Validation error"""

    def __init__(self, error: str, message: str):
        super().__init__(422, error, message)


class ServerError(HTTPError):
    """500 Server error"""

    def __init__(self, error: str, message: str):
        super().__init__(500, error, message)
