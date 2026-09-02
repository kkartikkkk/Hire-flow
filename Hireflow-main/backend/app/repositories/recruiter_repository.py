"""Recruiter repository — data access layer.

Provides database operations for Recruiter entities.
Contains no business logic — only queries.
"""

import uuid

from sqlalchemy.orm import Session

from app.models.recruiter import Recruiter
from app.repositories.base import BaseRepository


class RecruiterRepository(BaseRepository[Recruiter]):
    """Data access layer for Recruiter entities.

    Extends BaseRepository with recruiter-specific queries.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(model=Recruiter, db=db)

    def find_by_email(self, email: str) -> Recruiter | None:
        """Find a recruiter by their email address.

        Args:
            email: The email address to search for.

        Returns:
            The Recruiter instance or None if not found.
        """
        return (
            self.db.query(Recruiter)
            .filter(Recruiter.email == email)
            .first()
        )

    def find_by_id(self, recruiter_id: uuid.UUID) -> Recruiter | None:
        """Find a recruiter by their UUID.

        Args:
            recruiter_id: The UUID to search for.

        Returns:
            The Recruiter instance or None if not found.
        """
        return (
            self.db.query(Recruiter)
            .filter(Recruiter.id == recruiter_id)
            .first()
        )

    def exists_by_email(self, email: str) -> bool:
        """Check whether a recruiter with the given email exists.

        Args:
            email: The email address to check.

        Returns:
            True if a recruiter with this email exists, False otherwise.
        """
        return (
            self.db.query(Recruiter)
            .filter(Recruiter.email == email)
            .first()
            is not None
        )

    def create_recruiter(
        self,
        name: str,
        email: str,
        password_hash: str,
    ) -> Recruiter:
        """Create a new recruiter record.

        Args:
            name: Full name.
            email: Unique email address.
            password_hash: Bcrypt-hashed password.

        Returns:
            The newly created Recruiter instance with DB-generated fields.
        """
        recruiter = Recruiter(
            name=name,
            email=email,
            password_hash=password_hash,
        )
        return self.create(recruiter)
