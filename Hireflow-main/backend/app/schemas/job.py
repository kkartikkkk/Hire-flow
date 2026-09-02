"""Job management Pydantic schemas.

Defines request/response models for job CRUD, filtering, and list responses.
"""

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class JobStatusEnum(str, Enum):
    """Job status values for schema validation."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"


# ---- Request Schemas ----

class JobCreate(BaseModel):
    """Schema for creating a new job posting."""

    title: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Job title",
        examples=["Senior Python Developer"],
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Full job description",
        examples=["We are looking for an experienced Python developer..."],
    )
    required_skills: str = Field(
        ...,
        min_length=2,
        max_length=2000,
        description="Required skills (comma-separated)",
        examples=["Python, FastAPI, PostgreSQL, Docker"],
    )
    experience_required: int = Field(
        default=0,
        ge=0,
        le=50,
        description="Minimum years of experience",
        examples=[3],
    )
    location: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Job location",
        examples=["Remote"],
    )
    employment_type: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Employment type",
        examples=["Full-time"],
    )
    salary_range: str | None = Field(
        default=None,
        max_length=255,
        description="Salary range",
        examples=["$120,000 - $160,000"],
    )


class JobUpdate(BaseModel):
    """Schema for updating a job posting. All fields are optional."""

    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=255,
        description="Job title",
    )
    description: str | None = Field(
        default=None,
        min_length=10,
        max_length=5000,
        description="Full job description",
    )
    required_skills: str | None = Field(
        default=None,
        min_length=2,
        max_length=2000,
        description="Required skills",
    )
    experience_required: int | None = Field(
        default=None,
        ge=0,
        le=50,
        description="Minimum years of experience",
    )
    location: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
        description="Job location",
    )
    employment_type: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
        description="Employment type",
    )
    salary_range: str | None = Field(
        default=None,
        max_length=255,
        description="Salary range",
    )


class JobFilter(BaseModel):
    """Schema for job filtering query parameters."""

    status: JobStatusEnum | None = Field(default=None, description="Filter by status")
    location: str | None = Field(default=None, description="Filter by location")
    employment_type: str | None = Field(default=None, description="Filter by employment type")
    search: str | None = Field(default=None, description="Search in title, description, skills")


# ---- Response Schemas ----

class JobResponse(BaseModel):
    """Schema for a single job in API responses."""

    id: uuid.UUID
    recruiter_id: uuid.UUID
    title: str
    description: str
    required_skills: str
    experience_required: int
    location: str
    employment_type: str
    salary_range: str | None
    status: JobStatusEnum
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
