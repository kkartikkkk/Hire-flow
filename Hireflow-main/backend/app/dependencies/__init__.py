"""FastAPI dependency injection functions.

All Depends() callables used across route handlers are defined here.
"""

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db

__all__ = ["get_current_user", "get_db"]
