"""Application exception hierarchy and global exception handler.

All custom exceptions inherit from BaseAPIException.
The global handler converts them to structured JSON responses.
"""

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


class BaseAPIException(Exception):
    """Base exception for all application errors.

    Attributes:
        status_code: HTTP status code to return.
        detail: Human-readable error message.
        error_code: Machine-readable error identifier.
    """

    def __init__(
        self,
        status_code: int = 500,
        detail: str = "An unexpected error occurred",
        error_code: str = "INTERNAL_ERROR",
    ) -> None:
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        super().__init__(detail)


class AuthenticationException(BaseAPIException):
    """Raised when authentication fails."""

    def __init__(self, detail: str = "Authentication failed") -> None:
        super().__init__(status_code=401, detail=detail, error_code="AUTHENTICATION_ERROR")


class AuthorizationException(BaseAPIException):
    """Raised when the user lacks permissions."""

    def __init__(self, detail: str = "Insufficient permissions") -> None:
        super().__init__(status_code=403, detail=detail, error_code="AUTHORIZATION_ERROR")


class NotFoundException(BaseAPIException):
    """Raised when a requested resource is not found."""

    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(status_code=404, detail=detail, error_code="NOT_FOUND")


class ConflictException(BaseAPIException):
    """Raised when a resource already exists (e.g. duplicate email)."""

    def __init__(self, detail: str = "Resource already exists") -> None:
        super().__init__(status_code=409, detail=detail, error_code="CONFLICT")


class ValidationException(BaseAPIException):
    """Raised when input validation fails."""

    def __init__(self, detail: str = "Validation error") -> None:
        super().__init__(status_code=422, detail=detail, error_code="VALIDATION_ERROR")


class DatabaseException(BaseAPIException):
    """Raised when a database operation fails."""

    def __init__(self, detail: str = "Database error") -> None:
        super().__init__(status_code=500, detail=detail, error_code="DATABASE_ERROR")


class AIException(BaseAPIException):
    """Raised when an AI provider call fails."""

    def __init__(self, detail: str = "AI service error") -> None:
        super().__init__(status_code=503, detail=detail, error_code="AI_ERROR")


async def global_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """Convert BaseAPIException instances to structured JSON responses.

    Registered as a global exception handler in the FastAPI app.
    """
    logger.error(
        "API error: status=%d code=%s detail=%s path=%s",
        exc.status_code,
        exc.error_code,
        exc.detail,
        request.url.path,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.detail,
            }
        },
    )
