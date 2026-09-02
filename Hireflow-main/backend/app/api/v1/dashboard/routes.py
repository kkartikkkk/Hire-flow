"""Dashboard statistics API routes.

Provides aggregated recruitment metrics and recently created jobs/candidates.
All endpoints require JWT authorization.
"""

import uuid
from typing import Any
from fastapi import APIRouter, Depends, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.recruiter import Recruiter
from app.models.job import Job, JobStatus
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateResponse
from app.schemas.job import JobResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/stats",
    status_code=status.HTTP_200_OK,
    summary="Get recruiter dashboard statistics",
    description="Retrieve aggregated jobs, candidates, fit scores, and recent activities for the authenticated recruiter.",
    responses={
        200: {"description": "Dashboard statistics retrieved successfully"},
        401: {"description": "Not authenticated"},
    },
)
def get_dashboard_stats(
    current_user: Recruiter = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve recruiter-scoped metrics and recent lists."""
    recruiter_id = current_user.id

    # 1. Job statistics
    total_jobs = db.query(func.count(Job.id)).filter(Job.recruiter_id == recruiter_id).scalar() or 0
    open_jobs = db.query(func.count(Job.id)).filter(Job.recruiter_id == recruiter_id, Job.status == JobStatus.OPEN).scalar() or 0
    closed_jobs = db.query(func.count(Job.id)).filter(Job.recruiter_id == recruiter_id, Job.status == JobStatus.CLOSED).scalar() or 0

    # 2. Candidate statistics
    total_candidates = (
        db.query(func.count(Candidate.id))
        .join(Job, Candidate.job_id == Job.id)
        .filter(Job.recruiter_id == recruiter_id)
        .scalar() or 0
    )

    avg_fit_score = (
        db.query(func.avg(Candidate.fit_score))
        .join(Job, Candidate.job_id == Job.id)
        .filter(Job.recruiter_id == recruiter_id, Candidate.fit_score != None)
        .scalar()
    )
    if avg_fit_score is not None:
        avg_fit_score = round(float(avg_fit_score), 1)
    else:
        avg_fit_score = 0.0

    highest_fit_score = (
        db.query(func.max(Candidate.fit_score))
        .join(Job, Candidate.job_id == Job.id)
        .filter(Job.recruiter_id == recruiter_id, Candidate.fit_score != None)
        .scalar()
    )
    if highest_fit_score is None:
        highest_fit_score = 0

    # 3. Recent lists
    recent_jobs = (
        db.query(Job)
        .filter(Job.recruiter_id == recruiter_id)
        .order_by(Job.created_at.desc())
        .limit(5)
        .all()
    )

    recent_candidates = (
        db.query(Candidate)
        .join(Job, Candidate.job_id == Job.id)
        .filter(Job.recruiter_id == recruiter_id)
        .order_by(Candidate.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total_jobs": total_jobs,
        "open_jobs": open_jobs,
        "closed_jobs": closed_jobs,
        "total_candidates": total_candidates,
        "avg_fit_score": avg_fit_score,
        "highest_fit_score": highest_fit_score,
        "recent_jobs": [JobResponse.model_validate(j) for j in recent_jobs],
        "recent_candidates": [CandidateResponse.model_validate(c) for c in recent_candidates],
    }
