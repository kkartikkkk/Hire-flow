"""Authentication dependency.

Provides get_current_user for route-level JWT authentication.
Decodes the bearer token, extracts the sub claim, and queries
the database for the recruiter.
"""

import uuid

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationException
from app.core.security.jwt import decode_access_token
from app.dependencies.database import get_db
from app.models.recruiter import Recruiter
from app.repositories.recruiter_repository import RecruiterRepository
from app.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Recruiter:
    """Extract and validate the current user from the JWT bearer token.

    1. Decode the token and extract the 'sub' claim (recruiter UUID).
    2. Look up the recruiter in the database.
    3. Return the recruiter or raise 401.

    Args:
        token: JWT bearer token (injected by OAuth2PasswordBearer).
        db: Database session (injected by get_db).

    Returns:
        The authenticated Recruiter ORM instance.

    Raises:
        AuthenticationException: If the token is invalid or the user
            no longer exists.
    """
    payload = decode_access_token(token)

    sub: str | None = payload.get("sub")
    if sub is None:
        raise AuthenticationException(detail="Invalid token: missing subject")

    try:
        recruiter_id = uuid.UUID(sub)
    except ValueError as exc:
        raise AuthenticationException(detail="Invalid token: malformed subject") from exc

    repository = RecruiterRepository(db)
    service = AuthService(repository)
    return service.get_current_user(recruiter_id)
