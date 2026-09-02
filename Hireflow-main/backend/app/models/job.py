"""Job ORM model.

Defines the jobs table with UUID primary key, foreign key to recruiters,
full job posting fields, and indexed columns for filtering.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class JobStatus(str, enum.Enum):
    """Job posting status."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"


class Job(Base):
    """Job entity representing a job posting by a recruiter.

    Attributes:
        id: UUID primary key.
        recruiter_id: Foreign key to the owning recruiter.
        title: Job title.
        description: Full job description.
        required_skills: Comma-separated or freeform skills list.
        experience_required: Minimum years of experience.
        location: Job location.
        employment_type: Full-time, Part-time, Contract, etc.
        salary_range: Expected salary range (freeform text).
        status: OPEN or CLOSED.
        created_at: Timestamp of record creation.
        updated_at: Timestamp of last update.
    """

    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    recruiter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recruiters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    required_skills: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    experience_required: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    location: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    employment_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    salary_range: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status"),
        nullable=False,
        default=JobStatus.OPEN,
        index=True,
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
    recruiter = relationship("Recruiter", back_populates="jobs", lazy="select")
    candidates = relationship("Candidate", back_populates="job", cascade="all, delete-orphan", lazy="select")

    def __repr__(self) -> str:
        return f"<Job id={self.id} title={self.title} status={self.status}>"
