from typing import Optional, Dict, Any


class BaseAPIError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseAPIError):
    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 400, "VALIDATION_ERROR", details)


class AuthenticationError(BaseAPIError):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401, "AUTHENTICATION_ERROR")


class AuthorizationError(BaseAPIError):
    def __init__(self, message: str = "Not authorized to perform this action"):
        super().__init__(message, 403, "AUTHORIZATION_ERROR")


class NotFoundError(BaseAPIError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404, "NOT_FOUND")


class ConflictError(BaseAPIError):
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, 409, "CONFLICT_ERROR")


class DatabaseError(BaseAPIError):
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, 500, "DATABASE_ERROR")


class InternalServerError(BaseAPIError):
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, 500, "INTERNAL_SERVER_ERROR")
