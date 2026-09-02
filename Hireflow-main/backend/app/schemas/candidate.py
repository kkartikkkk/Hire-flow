"""Candidate schemas.

Defines schemas for candidate creation, updates, and responses with input validation.
"""

import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, field_validator


class CandidateStatusEnum(str, Enum):
    """Candidate application status values."""

    ACTIVE = "ACTIVE"
    SHORTLISTED = "SHORTLISTED"
    REJECTED = "REJECTED"
    HIRED = "HIRED"


class CandidateCreate(BaseModel):
    """Schema for creating a candidate."""

    job_id: uuid.UUID = Field(..., description="The ID of the job opening")
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Candidate's full name",
        examples=["John Doe"],
    )
    email: EmailStr = Field(
        ...,
        max_length=255,
        description="Candidate's email address",
        examples=["john.doe@example.com"],
    )
    phone: str = Field(
        ...,
        min_length=5,
        max_length=50,
        description="Candidate's phone number",
        examples=["+1-555-0199"],
    )
    resume_filename: str | None = Field(
        default=None,
        max_length=255,
        description="Name of the uploaded resume file",
    )
    skills: str = Field(
        ...,
        min_length=2,
        description="Technical skills of the candidate",
        examples=["Python, FastAPI, SQL"],
    )
    experience: str = Field(
        ...,
        min_length=2,
        description="Detailed work experience",
        examples=["3 years as Backend Developer at Tech Corp"],
    )
    education: str = Field(
        ...,
        min_length=2,
        description="Educational background details",
        examples=["B.S. in Computer Science from State University"],
    )
    fit_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
        description="Job fit score (0-100)",
    )
    fit_reason: str | None = Field(
        default=None,
        description="AI or recruiter fit reasoning",
    )
    status: CandidateStatusEnum = Field(
        default=CandidateStatusEnum.ACTIVE,
        description="Initial application status",
    )
    notes: str | None = Field(
        default=None,
        description="Recruiter notes",
    )

    @field_validator("phone")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        """Validate phone number format (allow digits, spaces, plus, hyphens, and parenthesis)."""
        cleaned = v.strip()
        # Allow numbers, optional +, -, spaces, parenthesis
        import re
        if not re.match(r"^\+?[\d\s\-\(\)]+$", cleaned):
            raise ValueError("Phone number must contain only numbers, spaces, +, -, or parenthesis")
        return cleaned


class CandidateUpdate(BaseModel):
    """Schema for updating a candidate's profile."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, min_length=5, max_length=50)
    resume_filename: str | None = Field(default=None, max_length=255)
    skills: str | None = Field(default=None, min_length=2)
    experience: str | None = Field(default=None, min_length=2)
    education: str | None = Field(default=None, min_length=2)
    fit_score: int | None = Field(default=None, ge=0, le=100)
    fit_reason: str | None = Field(default=None)
    status: CandidateStatusEnum | None = Field(default=None)
    notes: str | None = Field(default=None)
    parsed_resume: str | None = Field(default=None)
    parsed_at: datetime | None = Field(default=None)

    @field_validator("phone")
    @classmethod
    def validate_phone_number(cls, v: str | None) -> str | None:
        if v is None:
            return None
        cleaned = v.strip()
        import re
        if not re.match(r"^\+?[\d\s\-\(\)]+$", cleaned):
            raise ValueError("Phone number must contain only numbers, spaces, +, -, or parenthesis")
        return cleaned


class CandidateResponse(BaseModel):
    """Response schema for a single candidate."""

    id: uuid.UUID
    job_id: uuid.UUID
    name: str
    email: str
    phone: str
    resume_filename: str | None
    skills: str
    experience: str
    education: str
    fit_score: int | None
    fit_reason: str | None
    status: CandidateStatusEnum
    notes: str | None
    parsed_resume: str | None
    parsed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
