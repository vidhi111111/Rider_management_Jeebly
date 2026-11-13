"""Custom application exceptions for structured error handling across modules."""
from typing import Optional, Dict, Any


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = 400, data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.data = data


class ValidationAppError(AppException):
    """Raised when request payload validation fails."""

    def __init__(self, message: str = "Validation failed.", errors: Optional[Dict[str, str]] = None):
        super().__init__(message, status_code=400, data={"errors": errors} if errors else None)
        self.errors = errors or {}


class ResourceNotFoundError(AppException):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found."):
        super().__init__(message, status_code=404)


class ConflictAppError(AppException):
    """Raised when a unique constraint or conflict occurs (e.g. duplicate email/phone)."""

    def __init__(self, message: str = "Resource conflict."):
        super().__init__(message, status_code=409)


class UnauthorizedAppError(AppException):
    """Raised when authentication credentials are missing or invalid."""

    def __init__(self, message: str = "Unauthorized."):
        super().__init__(message, status_code=401)
