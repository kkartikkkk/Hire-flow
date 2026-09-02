import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.job import Job, JobStatus
from app.models.candidate import Candidate, CandidateStatus


def test_get_dashboard_stats_empty(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """Verify stats returns zeros when there are no jobs or candidates."""
    response = client.get("/api/v1/dashboard/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_jobs"] == 0
    assert data["open_jobs"] == 0
    assert data["closed_jobs"] == 0
    assert data["total_candidates"] == 0
    assert data["avg_fit_score"] == 0.0
    assert data["highest_fit_score"] == 0
    assert len(data["recent_jobs"]) == 0
    assert len(data["recent_candidates"]) == 0


def test_get_dashboard_stats_populated(
    client: TestClient,
    db_session: Session,
    auth_headers: dict[str, str],
) -> None:
    """Verify stats returns correct aggregated metrics."""
    # Find recruiter ID from current token or DB
    from app.models.recruiter import Recruiter
    recruiter = db_session.query(Recruiter).first()
    assert recruiter is not None

    # Create job
    job = Job(
        recruiter_id=recruiter.id,
        title="Frontend Architect",
        description="Core layouts expert",
        required_skills="React, CSS",
        experience_required=5,
        location="Remote",
        employment_type="FULL_TIME",
        status=JobStatus.OPEN,
    )
    db_session.add(job)
    db_session.commit()

    # Create candidate
    cand = Candidate(
        job_id=job.id,
        name="Bob",
        email="bob@example.com",
        phone="555-1234",
        skills="React, CSS",
        experience="5 years",
        education="B.S.",
        status=CandidateStatus.ACTIVE,
        fit_score=85,
        fit_reason="Strong matches",
    )
    db_session.add(cand)
    db_session.commit()

    response = client.get("/api/v1/dashboard/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_jobs"] == 1
    assert data["open_jobs"] == 1
    assert data["total_candidates"] == 1
    assert data["avg_fit_score"] == 85.0
    assert data["highest_fit_score"] == 85
    assert len(data["recent_jobs"]) == 1
    assert len(data["recent_candidates"]) == 1
