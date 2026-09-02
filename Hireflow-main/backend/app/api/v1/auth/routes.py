"""Authentication API routes.

Provides endpoints for recruiter registration, login,
and current user retrieval.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.recruiter import Recruiter
from app.repositories.recruiter_repository import RecruiterRepository
from app.schemas.auth import (
    CurrentUserResponse,
    RecruiterCreate,
    RecruiterLogin,
    RecruiterResponse,
    TokenResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Construct AuthService with injected repository.

    This is a route-level dependency that wires the service layer.
    """
    repository = RecruiterRepository(db)
    return AuthService(repository)


@router.post(
    "/register",
    response_model=RecruiterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new recruiter",
    description=(
        "Create a new recruiter account. Returns the recruiter profile "
        "and a JWT access token in the response."
    ),
    responses={
        201: {"description": "Recruiter created successfully"},
        409: {"description": "Email already registered"},
        422: {"description": "Validation error"},
    },
)
def register(
    data: RecruiterCreate,
    service: AuthService = Depends(_get_auth_service),
) -> RecruiterResponse:
    """Register a new recruiter account.

    Validates input, checks for duplicate email, hashes password,
    creates the recruiter, and returns the profile.
    """
    recruiter, _token = service.register(data)
    return RecruiterResponse.model_validate(recruiter)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login recruiter",
    description=(
        "Authenticate with email and password. "
        "Returns a JWT access token on success."
    ),
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
        422: {"description": "Validation error"},
    },
)
def login(
    data: RecruiterLogin,
    service: AuthService = Depends(_get_auth_service),
) -> TokenResponse:
    """Authenticate a recruiter and issue a JWT token.

    Verifies email and password, then returns a bearer token.
    """
    _recruiter, token = service.login(data)
    return token


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    summary="Get current user",
    description="Retrieve the profile of the currently authenticated recruiter.",
    responses={
        200: {"description": "Current user profile"},
        401: {"description": "Not authenticated or invalid token"},
    },
)
def get_me(
    current_user: Recruiter = Depends(get_current_user),
) -> CurrentUserResponse:
    """Return the profile of the authenticated recruiter.

    Requires a valid JWT bearer token.
    """
    return CurrentUserResponse.model_validate(current_user)
