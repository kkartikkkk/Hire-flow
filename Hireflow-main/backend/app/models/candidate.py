"""Candidate ORM model.

Defines the candidates table with UUID primary key, foreign key to jobs,
fields for candidate profile information, and indexes for filtering.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class CandidateStatus(str, enum.Enum):
    """Status of a candidate's application."""

    ACTIVE = "ACTIVE"
    SHORTLISTED = "SHORTLISTED"
    REJECTED = "REJECTED"
    HIRED = "HIRED"


class Candidate(Base):
    """Candidate entity representing a job applicant.

    Attributes:
        id: UUID primary key.
        job_id: Foreign key to the applied job.
        name: Candidate's full name.
        email: Candidate's email address.
        phone: Candidate's phone number.
        resume_filename: Name of the resume file (optional).
        skills: Technical skills list or description.
        experience: Work experience details.
        education: Educational background details.
        fit_score: AI-calculated or manual fit score (optional).
        fit_reason: Detailed explanation of the fit score (optional).
        status: ACTIVE, SHORTLISTED, REJECTED, or HIRED.
        notes: Recruiter notes about the candidate.
        created_at: Timestamp of record creation.
        updated_at: Timestamp of last update.
    """

    __tablename__ = "candidates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    phone: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    resume_filename: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    skills: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    experience: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    education: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    fit_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    fit_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[CandidateStatus] = mapped_column(
        Enum(CandidateStatus, name="candidate_status"),
        nullable=False,
        default=CandidateStatus.ACTIVE,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    parsed_resume: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    parsed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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
    job = relationship("Job", back_populates="candidates", lazy="select")

    def __repr__(self) -> str:
        return f"<Candidate id={self.id} name={self.name} status={self.status}>"
