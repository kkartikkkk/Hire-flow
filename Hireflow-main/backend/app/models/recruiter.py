"""Recruiter ORM model.

Defines the recruiters table with UUID primary key, email uniqueness,
and password hash storage.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Recruiter(Base):
    """Recruiter entity representing an authenticated user.

    Attributes:
        id: UUID primary key.
        name: Full name of the recruiter.
        email: Unique email address used for login.
        password_hash: Bcrypt-hashed password (never stored in plain text).
        created_at: Timestamp of record creation.
        updated_at: Timestamp of last update.
    """

    __tablename__ = "recruiters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ---- Relationships ----
    jobs = relationship("Job", back_populates="recruiter", lazy="select")

    def __repr__(self) -> str:
        return f"<Recruiter id={self.id} email={self.email}>"
