"""Candidate management API routes.

Provides endpoints for candidate CRUD, search, filtering, and pagination.
All endpoints require JWT authentication and verify recruiter ownership.
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.recruiter import Recruiter
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.job_repository import JobRepository
from app.schemas.common import PaginatedResponse
from app.schemas.candidate import CandidateCreate, CandidateResponse, CandidateStatusEnum, CandidateUpdate
from app.services.candidate_service import CandidateService

router = APIRouter(prefix="/candidates", tags=["Candidates"])


def _get_candidate_service(db: Session = Depends(get_db)) -> CandidateService:
    """Construct CandidateService."""
    from app.services.resume_parser_service import ResumeParserService
    from app.services.fit_score_service import FitScoreService
    from app.ai.factory import get_ai_provider

    ai_provider = get_ai_provider()
    return CandidateService(
        repository=CandidateRepository(db),
        job_repository=JobRepository(db),
        parser_service=ResumeParserService(ai_provider),
        score_service=FitScoreService(ai_provider),
    )


@router.post(
    "",
    response_model=CandidateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a candidate",
    description="Create a new candidate application for a job owned by the authenticated recruiter.",
    responses={
        201: {"description": "Candidate created successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to access the job"},
        404: {"description": "Job not found"},
        422: {"description": "Validation error"},
    },
)
def create_candidate(
    data: CandidateCreate,
    current_user: Recruiter = Depends(get_current_user),
    service: CandidateService = Depends(_get_candidate_service),
) -> CandidateResponse:
    """Create a new candidate application."""
    candidate = service.create_candidate(current_user.id, data)
    return CandidateResponse.model_validate(candidate)


@router.get(
    "",
    response_model=PaginatedResponse[CandidateResponse],
    summary="List candidates",
    description="Retrieve a paginated, filterable list of all candidates applying to jobs owned by the recruiter.",
    responses={
        200: {"description": "Paginated list of candidates"},
        401: {"description": "Not authenticated"},
    },
)
def list_candidates(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    status_filter: CandidateStatusEnum | None = Query(default=None, alias="status", description="Filter by candidate status"),
    job_id: uuid.UUID | None = Query(default=None, description="Filter by job ID"),
    experience: str | None = Query(default=None, description="Filter by experience text"),
    created_date: date | None = Query(default=None, description="Filter by creation date (YYYY-MM-DD)"),
    search: str | None = Query(default=None, description="Search in name, email, phone, or skills"),
    current_user: Recruiter = Depends(get_current_user),
    service: CandidateService = Depends(_get_candidate_service),
) -> PaginatedResponse[CandidateResponse]:
    """List candidates belonging to the recruiter's job openings."""
    result = service.list_candidates(
        recruiter_id=current_user.id,
        page=page,
        page_size=page_size,
        status=status_filter,
        job_id=job_id,
        experience=experience,
        created_date=created_date,
        search=search,
    )
    result["items"] = [CandidateResponse.model_validate(c) for c in result["items"]]
    return PaginatedResponse[CandidateResponse](**result)


@router.get(
    "/{candidate_id}",
    response_model=CandidateResponse,
    summary="Get candidate details",
    description="Retrieve the details of a candidate, checking recruiter ownership of their job posting.",
    responses={
        200: {"description": "Candidate details retrieved successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to access this candidate"},
        404: {"description": "Candidate not found"},
    },
)
def get_candidate(
    candidate_id: uuid.UUID,
    current_user: Recruiter = Depends(get_current_user),
    service: CandidateService = Depends(_get_candidate_service),
) -> CandidateResponse:
    """Retrieve detailed candidate profile."""
    candidate = service.get_candidate(current_user.id, candidate_id)
    return CandidateResponse.model_validate(candidate)


@router.put(
    "/{candidate_id}",
    response_model=CandidateResponse,
    summary="Update a candidate",
    description="Update a candidate's profile, including details, skills, notes, or application status.",
    responses={
        200: {"description": "Candidate updated successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to modify this candidate"},
        404: {"description": "Candidate not found"},
        422: {"description": "Validation error"},
    },
)
def update_candidate(
    candidate_id: uuid.UUID,
    data: CandidateUpdate,
    current_user: Recruiter = Depends(get_current_user),
    service: CandidateService = Depends(_get_candidate_service),
) -> CandidateResponse:
    """Update candidate profile details."""
    candidate = service.update_candidate(current_user.id, candidate_id, data)
    return CandidateResponse.model_validate(candidate)


@router.delete(
    "/{candidate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete candidate",
    description="Permanently delete a candidate application from the system.",
    responses={
        204: {"description": "Candidate deleted successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to delete this candidate"},
        404: {"description": "Candidate not found"},
    },
)
def delete_candidate(
    candidate_id: uuid.UUID,
    current_user: Recruiter = Depends(get_current_user),
    service: CandidateService = Depends(_get_candidate_service),
) -> None:
    """Permanently delete a candidate."""
    service.delete_candidate(current_user.id, candidate_id)


@router.post(
    "/upload",
    response_model=CandidateResponse,
    summary="Upload candidate resume",
    description="Upload a PDF or DOCX resume document for a candidate.",
    responses={
        200: {"description": "Resume uploaded and text extracted successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to access this candidate"},
        404: {"description": "Candidate not found"},
        422: {"description": "Validation error (invalid file size, extension, or MIME type)"},
    },
)
async def upload_resume(
    candidate_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    current_user: Recruiter = Depends(get_current_user),
    service: CandidateService = Depends(_get_candidate_service),
) -> CandidateResponse:
    """Upload a candidate resume document."""
    candidate = await service.save_resume_upload(candidate_id, file, current_user.id)
    return CandidateResponse.model_validate(candidate)


@router.post(
    "/{candidate_id}/parse",
    response_model=CandidateResponse,
    summary="Parse candidate resume",
    description="Trigger AI parsing of the candidate's uploaded resume document.",
    responses={
        200: {"description": "Resume parsed successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to access this candidate"},
        404: {"description": "Candidate not found"},
        503: {"description": "AI service currently unavailable"},
    },
)
async def parse_resume(
    candidate_id: uuid.UUID,
    current_user: Recruiter = Depends(get_current_user),
    service: CandidateService = Depends(_get_candidate_service),
) -> CandidateResponse:
    """Parse candidate resume using AI."""
    candidate = await service.parse_candidate_resume(candidate_id, current_user.id)
    return CandidateResponse.model_validate(candidate)


@router.post(
    "/{candidate_id}/fit-score",
    response_model=CandidateResponse,
    summary="Generate candidate fit score",
    description="Compare the candidate's details against their associated job opening to generate an AI fit score report.",
    responses={
        200: {"description": "Fit score generated successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to access this candidate"},
        404: {"description": "Candidate or Job not found"},
        503: {"description": "AI service currently unavailable"},
    },
)
async def calculate_fit_score(
    candidate_id: uuid.UUID,
    current_user: Recruiter = Depends(get_current_user),
    service: CandidateService = Depends(_get_candidate_service),
) -> CandidateResponse:
    """Calculate candidate fit score using AI."""
    candidate = await service.calculate_candidate_fit_score(candidate_id, current_user.id)
    return CandidateResponse.model_validate(candidate)


@router.get(
    "/{candidate_id}/parsed",
    response_model=CandidateResponse,
    summary="Get parsed resume details",
    description="Retrieve parsed resume details and fit scoring reports for a candidate.",
    responses={
        200: {"description": "Parsed candidate details retrieved successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to access this candidate"},
        404: {"description": "Candidate not found"},
    },
)
def get_parsed_candidate(
    candidate_id: uuid.UUID,
    current_user: Recruiter = Depends(get_current_user),
    service: CandidateService = Depends(_get_candidate_service),
) -> CandidateResponse:
    """Get parsed resume details for a candidate."""
    candidate = service.get_candidate(current_user.id, candidate_id)
    return CandidateResponse.model_validate(candidate)


@router.post(
    "/upload-direct",
    response_model=CandidateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Directly upload and parse resume to create candidate",
    description="Upload a resume file (PDF/DOCX) to automatically create a candidate and generate their fit score report.",
    responses={
        201: {"description": "Candidate created and resume parsed successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized to access the job opening"},
        404: {"description": "Job opening not found"},
        422: {"description": "Validation error (invalid file size, extension, or MIME type)"},
    },
)
async def upload_direct(
    job_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    current_user: Recruiter = Depends(get_current_user),
    service: CandidateService = Depends(_get_candidate_service),
) -> CandidateResponse:
    """Directly create candidate via resume file upload and AI parsing."""
    candidate = await service.create_candidate_from_resume(
        recruiter_id=current_user.id,
        job_id=job_id,
        file=file,
    )
    return CandidateResponse.model_validate(candidate)
