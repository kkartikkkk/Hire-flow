"""JWT token creation and verification utilities.

Uses python-jose for token operations.
Configuration is read from centralized settings.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import get_settings
from app.core.exceptions import AuthenticationException
from app.core.logging import get_logger

logger = get_logger(__name__)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token.

    Args:
        data: Payload data to encode in the token.
        expires_delta: Optional custom expiration. Defaults to settings.JWT_EXPIRE_MINUTES.

    Returns:
        Encoded JWT string.
    """
    settings = get_settings()
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    )
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    })

    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token.

    Args:
        token: The JWT string to decode.

    Returns:
        Decoded payload dictionary.

    Raises:
        AuthenticationException: If the token is invalid or expired.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as exc:
        logger.warning("JWT decode failed: %s", exc)
        raise AuthenticationException(detail="Invalid or expired token") from exc
