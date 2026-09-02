"""Authentication service — business logic layer.

Handles recruiter registration, login, token generation,
and current user retrieval. All database access is delegated
to RecruiterRepository.
"""

import uuid

from app.core.exceptions import AuthenticationException, ConflictException
from app.core.logging import get_logger
from app.core.security.jwt import create_access_token
from app.core.security.password import hash_password, verify_password
from app.models.recruiter import Recruiter
from app.repositories.recruiter_repository import RecruiterRepository
from app.schemas.auth import RecruiterCreate, RecruiterLogin, TokenResponse

logger = get_logger(__name__)


class AuthService:
    """Business logic for authentication operations.

    All database access is delegated to the injected repository.
    This service handles:
    - Recruiter registration (with duplicate check and password hashing)
    - Recruiter login (with credential verification and token generation)
    - Current user retrieval by UUID
    """

    def __init__(self, repository: RecruiterRepository) -> None:
        self.repository = repository

    def register(self, data: RecruiterCreate) -> tuple[Recruiter, TokenResponse]:
        """Register a new recruiter.

        Args:
            data: Validated registration data.

        Returns:
            Tuple of (created Recruiter, TokenResponse).

        Raises:
            ConflictException: If the email is already registered.
        """
        if self.repository.exists_by_email(data.email):
            logger.warning("Registration failed — duplicate email: %s", data.email)
            raise ConflictException(detail="A recruiter with this email already exists")

        hashed = hash_password(data.password)

        recruiter = self.repository.create_recruiter(
            name=data.name,
            email=data.email,
            password_hash=hashed,
        )

        logger.info("Recruiter registered: id=%s email=%s", recruiter.id, recruiter.email)

        token = self._generate_token(recruiter)
        return recruiter, token

    def login(self, data: RecruiterLogin) -> tuple[Recruiter, TokenResponse]:
        """Authenticate a recruiter and issue a JWT token.

        Args:
            data: Validated login credentials.

        Returns:
            Tuple of (authenticated Recruiter, TokenResponse).

        Raises:
            AuthenticationException: If credentials are invalid.
        """
        recruiter = self.repository.find_by_email(data.email)

        if recruiter is None:
            logger.warning("Login failed — email not found: %s", data.email)
            raise AuthenticationException(detail="Invalid email or password")

        if not verify_password(data.password, recruiter.password_hash):
            logger.warning("Login failed — wrong password for: %s", data.email)
            raise AuthenticationException(detail="Invalid email or password")

        logger.info("Recruiter logged in: id=%s email=%s", recruiter.id, recruiter.email)

        token = self._generate_token(recruiter)
        return recruiter, token

    def get_current_user(self, recruiter_id: uuid.UUID) -> Recruiter:
        """Retrieve a recruiter by their UUID.

        Used by the authentication dependency after token decoding.

        Args:
            recruiter_id: The UUID extracted from the JWT sub claim.

        Returns:
            The Recruiter instance.

        Raises:
            AuthenticationException: If the recruiter no longer exists.
        """
        recruiter = self.repository.find_by_id(recruiter_id)

        if recruiter is None:
            logger.warning("Token valid but recruiter not found: %s", recruiter_id)
            raise AuthenticationException(detail="User not found")

        return recruiter

    @staticmethod
    def _generate_token(recruiter: Recruiter) -> TokenResponse:
        """Generate a JWT access token for the given recruiter.

        The sub claim is the recruiter's UUID as a string.

        Args:
            recruiter: The authenticated recruiter.

        Returns:
            TokenResponse with the encoded JWT.
        """
        access_token = create_access_token(data={"sub": str(recruiter.id)})
        return TokenResponse(access_token=access_token)
