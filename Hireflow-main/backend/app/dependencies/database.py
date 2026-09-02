"""Database session dependency.

Re-exports get_db from the database package for use in Depends().
"""

from app.database.session import get_db

__all__ = ["get_db"]
