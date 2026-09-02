"""Authentication Pydantic schemas.

Defines request/response models for registration, login,
token responses, and current user endpoints.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ---- Request Schemas ----

class RecruiterCreate(BaseModel):
    """Schema for recruiter registration request."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Full name of the recruiter",
        examples=["Anurag Singh"],
    )
    email: EmailStr = Field(
        ...,
        description="Email address (must be unique)",
        examples=["anurag@gappeo.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (minimum 8 characters)",
        examples=["SecurePass123"],
    )


class RecruiterLogin(BaseModel):
    """Schema for recruiter login request."""

    email: EmailStr = Field(
        ...,
        description="Registered email address",
        examples=["anurag@gappeo.com"],
    )
    password: str = Field(
        ...,
        min_length=1,
        description="Account password",
        examples=["SecurePass123"],
    )


# ---- Response Schemas ----

class RecruiterResponse(BaseModel):
    """Schema for recruiter data in responses (excludes password)."""

    id: uuid.UUID
    name: str
    email: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Schema for JWT token response after login/registration."""

    access_token: str
    token_type: str = "bearer"


class CurrentUserResponse(BaseModel):
    """Schema for the /auth/me endpoint response."""

    id: uuid.UUID
    name: str
    email: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
