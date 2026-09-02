"""Job management API routes.

Provides CRUD endpoints for job postings. All endpoints require
JWT authentication and enforce job ownership.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.recruiter import Recruiter
from app.repositories.job_repository import JobRepository
from app.schemas.common import PaginatedResponse
from app.schemas.job import JobCreate, JobResponse, JobUpdate
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["Jobs"])


def _get_job_service(db: Session = Depends(get_db)) -> JobService:
    """Construct JobService with injected repository."""
    return JobService(JobRepository(db))


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a job posting",
    description="Create a new job posting for the authenticated recruiter.",
    responses={
        201: {"description": "Job created successfully"},
        401: {"description": "Not authenticated"},
        422: {"description": "Validation error"},
    },
)
def create_job(
    data: JobCreate,
    current_user: Recruiter = Depends(get_current_user),
    service: JobService = Depends(_get_job_service),
) -> JobResponse:
    """Create a new job posting."""
    job = service.create_job(current_user.id, data)
    return JobResponse.model_validate(job)


@router.get(
    "",
    response_model=PaginatedResponse[JobResponse],
    summary="List jobs",
    description=(
        "Retrieve a paginated list of the authenticated recruiter's jobs. "
        "Supports filtering by status, location, employment type, and text search."
    ),
    responses={
        200: {"description": "Paginated job list"},
        401: {"description": "Not authenticated"},
    },
)
def list_jobs(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    status_filter: str | None = Query(default=None, alias="status", description="Filter by status (OPEN/CLOSED)"),
    location: str | None = Query(default=None, description="Filter by location"),
    employment_type: str | None = Query(default=None, description="Filter by employment type"),
    search: str | None = Query(default=None, description="Search title, description, skills"),
    current_user: Recruiter = Depends(get_current_user),
    service: JobService = Depends(_get_job_service),
) -> PaginatedResponse[JobResponse]:
    """List the authenticated recruiter's jobs with filters and pagination."""
    result = service.list_jobs(
        recruiter_id=current_user.id,
        page=page,
        page_size=page_size,
        status=status_filter,
        location=location,
        employment_type=employment_type,
        search=search,
    )
    result["items"] = [JobResponse.model_validate(j) for j in result["items"]]
    return PaginatedResponse[JobResponse](**result)


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get a job",
    description="Retrieve a single job posting by ID.",
    responses={
        200: {"description": "Job details"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not the job owner"},
        404: {"description": "Job not found"},
    },
)
def get_job(
    job_id: uuid.UUID,
    current_user: Recruiter = Depends(get_current_user),
    service: JobService = Depends(_get_job_service),
) -> JobResponse:
    """Get a single job by ID (ownership enforced)."""
    job = service.get_job(job_id, current_user.id)
    return JobResponse.model_validate(job)


@router.put(
    "/{job_id}",
    response_model=JobResponse,
    summary="Update a job",
    description="Update a job posting. Closed jobs cannot be edited.",
    responses={
        200: {"description": "Job updated"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not the job owner"},
        404: {"description": "Job not found"},
        422: {"description": "Validation error or job is closed"},
    },
)
def update_job(
    job_id: uuid.UUID,
    data: JobUpdate,
    current_user: Recruiter = Depends(get_current_user),
    service: JobService = Depends(_get_job_service),
) -> JobResponse:
    """Update a job posting (ownership enforced, blocks closed jobs)."""
    job = service.update_job(job_id, current_user.id, data)
    return JobResponse.model_validate(job)


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a job",
    description="Permanently delete a job posting.",
    responses={
        204: {"description": "Job deleted"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not the job owner"},
        404: {"description": "Job not found"},
    },
)
def delete_job(
    job_id: uuid.UUID,
    current_user: Recruiter = Depends(get_current_user),
    service: JobService = Depends(_get_job_service),
) -> None:
    """Delete a job posting (ownership enforced)."""
    service.delete_job(job_id, current_user.id)


@router.patch(
    "/{job_id}/close",
    response_model=JobResponse,
    summary="Close a job",
    description="Close an open job posting. Already-closed jobs return a validation error.",
    responses={
        200: {"description": "Job closed"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not the job owner"},
        404: {"description": "Job not found"},
        422: {"description": "Job is already closed"},
    },
)
def close_job(
    job_id: uuid.UUID,
    current_user: Recruiter = Depends(get_current_user),
    service: JobService = Depends(_get_job_service),
) -> JobResponse:
    """Close a job posting (ownership enforced)."""
    job = service.close_job(job_id, current_user.id)
    return JobResponse.model_validate(job)

