"""Integration and unit tests for the Candidate Management module.

Verifies candidate CRUD operations, database mapping, status transitions,
ownership constraints, search, and filtering.
"""

import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.candidate import Candidate, CandidateStatus
from app.models.job import Job
from app.models.recruiter import Recruiter


def test_create_candidate_success(
    client: TestClient,
    db_session: Session,
    test_job: Job,
    auth_headers: dict[str, str],
) -> None:
    """Verify that a recruiter can successfully create a candidate for their job."""
    payload = {
        "job_id": str(test_job.id),
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-0199",
        "skills": "Python, FastAPI, Docker",
        "experience": "3 years of backend experience",
        "education": "B.S. in Computer Science",
        "notes": "Strong candidate",
    }

    response = client.post(
        "/api/v1/candidates",
        headers=auth_headers,
        json=payload,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john.doe@example.com"
    assert data["status"] == "ACTIVE"
    assert data["job_id"] == str(test_job.id)

    # Check database
    candidate = db_session.query(Candidate).filter(Candidate.id == uuid.UUID(data["id"])).first()
    assert candidate is not None
    assert candidate.name == "John Doe"


def test_create_candidate_validation_errors(
    client: TestClient,
    test_job: Job,
    auth_headers: dict[str, str],
) -> None:
    """Verify field validations (email, phone, min_length) on creation."""
    # Invalid email and phone
    payload = {
        "job_id": str(test_job.id),
        "name": "",
        "email": "not-an-email",
        "phone": "invalid-phone-char$",
        "skills": "Go",
        "experience": "1 yr",
        "education": "BS",
    }

    response = client.post(
        "/api/v1/candidates",
        headers=auth_headers,
        json=payload,
    )
    assert response.status_code == 422


def test_create_candidate_forbidden_job(
    client: TestClient,
    db_session: Session,
    auth_headers: dict[str, str],
) -> None:
    """Verify a recruiter cannot add candidates to another recruiter's job."""
    other_recruiter = Recruiter(
        name="Other Recruiter",
        email=f"other_{uuid.uuid4()}@example.com",
        password_hash="...",
    )
    db_session.add(other_recruiter)
    db_session.commit()

    other_job = Job(
        recruiter_id=other_recruiter.id,
        title="Other Job",
        description="...",
        required_skills="...",
        location="...",
        employment_type="...",
    )
    db_session.add(other_job)
    db_session.commit()

    payload = {
        "job_id": str(other_job.id),
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "1234567890",
        "skills": "Python",
        "experience": "2 years",
        "education": "MS",
    }

    response = client.post(
        "/api/v1/candidates",
        headers=auth_headers,
        json=payload,
    )
    assert response.status_code == 403


def test_list_candidates_for_recruiter(
    client: TestClient,
    db_session: Session,
    test_job: Job,
    auth_headers: dict[str, str],
) -> None:
    """Verify listing and pagination of recruiter's candidates."""
    cand1 = Candidate(
        job_id=test_job.id,
        name="Alice",
        email="alice@example.com",
        phone="111-222-3333",
        skills="Python",
        experience="3 years",
        education="B.S.",
        status=CandidateStatus.ACTIVE,
    )
    cand2 = Candidate(
        job_id=test_job.id,
        name="Bob",
        email="bob@example.com",
        phone="444-555-6666",
        skills="FastAPI",
        experience="5 years",
        education="M.S.",
        status=CandidateStatus.SHORTLISTED,
    )
    db_session.add_all([cand1, cand2])
    db_session.commit()

    response = client.get(
        "/api/v1/candidates",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 2


def test_list_candidates_search_and_filters(
    client: TestClient,
    db_session: Session,
    test_job: Job,
    auth_headers: dict[str, str],
) -> None:
    """Verify search (skills) and filtering (status, experience)."""
    cand1 = Candidate(
        job_id=test_job.id,
        name="Alice",
        email="alice@example.com",
        phone="111-222-3333",
        skills="Python",
        experience="Senior Analyst",
        education="B.S.",
        status=CandidateStatus.ACTIVE,
    )
    cand2 = Candidate(
        job_id=test_job.id,
        name="Bob",
        email="bob@example.com",
        phone="444-555-6666",
        skills="React",
        experience="Junior Dev",
        education="M.S.",
        status=CandidateStatus.SHORTLISTED,
    )
    db_session.add_all([cand1, cand2])
    db_session.commit()

    # Search for React
    response = client.get(
        "/api/v1/candidates?search=react",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["name"] == "Bob"

    # Filter by status
    response = client.get(
        "/api/v1/candidates?status=SHORTLISTED",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1

    # Filter by experience
    response = client.get(
        "/api/v1/candidates?experience=Senior",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["name"] == "Alice"


def test_get_candidate_by_id(
    client: TestClient,
    db_session: Session,
    test_job: Job,
    auth_headers: dict[str, str],
) -> None:
    """Verify fetching candidate details."""
    cand = Candidate(
        job_id=test_job.id,
        name="Alice",
        email="alice@example.com",
        phone="111-222-3333",
        skills="Python",
        experience="3 years",
        education="B.S.",
        status=CandidateStatus.ACTIVE,
    )
    db_session.add(cand)
    db_session.commit()

    response = client.get(
        f"/api/v1/candidates/{cand.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Alice"


def test_update_candidate(
    client: TestClient,
    db_session: Session,
    test_job: Job,
    auth_headers: dict[str, str],
) -> None:
    """Verify updating candidate profile information."""
    cand = Candidate(
        job_id=test_job.id,
        name="Alice",
        email="alice@example.com",
        phone="111-222-3333",
        skills="Python",
        experience="3 years",
        education="B.S.",
        status=CandidateStatus.ACTIVE,
    )
    db_session.add(cand)
    db_session.commit()

    payload = {
        "name": "Alice Cooper",
        "status": "SHORTLISTED",
        "notes": "Excellent interview",
    }

    response = client.put(
        f"/api/v1/candidates/{cand.id}",
        headers=auth_headers,
        json=payload,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Alice Cooper"
    assert response.json()["status"] == "SHORTLISTED"


def test_delete_candidate(
    client: TestClient,
    db_session: Session,
    test_job: Job,
    auth_headers: dict[str, str],
) -> None:
    """Verify candidate deletion."""
    cand = Candidate(
        job_id=test_job.id,
        name="Alice",
        email="alice@example.com",
        phone="111-222-3333",
        skills="Python",
        experience="3 years",
        education="B.S.",
        status=CandidateStatus.ACTIVE,
    )
    db_session.add(cand)
    db_session.commit()

    response = client.delete(
        f"/api/v1/candidates/{cand.id}",
        headers=auth_headers,
    )
    assert response.status_code == 204

    # Verify database
    db_cand = db_session.query(Candidate).filter(Candidate.id == cand.id).first()
    assert db_cand is None


def test_upload_resume_pdf_success(
    client: TestClient,
    db_session: Session,
    test_job: Job,
    auth_headers: dict[str, str],
) -> None:
    """Verify that a recruiter can upload a PDF resume for their candidate."""
    cand = Candidate(
        job_id=test_job.id,
        name="Alice",
        email="alice@example.com",
        phone="111-222-3333",
        skills="Python",
        experience="3 years",
        education="B.S.",
        status=CandidateStatus.ACTIVE,
    )
    db_session.add(cand)
    db_session.commit()

    import io
    pdf_content = b"%PDF-1.4 mock pdf content"
    files = {
        "file": ("test_resume.pdf", io.BytesIO(pdf_content), "application/pdf")
    }
    data = {
        "candidate_id": str(cand.id)
    }

    from unittest.mock import patch, MagicMock
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "Candidate Resume Text Python FastAPI Developer"
    mock_doc.__iter__.return_value = [mock_page]

    with patch("fitz.open", return_value=mock_doc):
        response = client.post(
            "/api/v1/candidates/upload",
            headers=auth_headers,
            data=data,
            files=files,
        )

    assert response.status_code == 200
    res_data = response.json()
    assert res_data["resume_filename"] == "test_resume.pdf"
    assert res_data["parsed_resume"] == "Candidate Resume Text Python FastAPI Developer"


def test_upload_resume_invalid_mime_type(
    client: TestClient,
    db_session: Session,
    test_job: Job,
    auth_headers: dict[str, str],
) -> None:
    """Verify upload rejects invalid MIME type."""
    cand = Candidate(
        job_id=test_job.id,
        name="Alice",
        email="alice@example.com",
        phone="111-222-3333",
        skills="Python",
        experience="3 years",
        education="B.S.",
        status=CandidateStatus.ACTIVE,
    )
    db_session.add(cand)
    db_session.commit()

    import io
    files = {
        "file": ("test_resume.pdf", io.BytesIO(b"data"), "text/plain")
    }
    data = {"candidate_id": str(cand.id)}

    response = client.post(
        "/api/v1/candidates/upload",
        headers=auth_headers,
        data=data,
        files=files,
    )
    assert response.status_code == 422
    assert "Invalid MIME type" in response.json()["error"]["message"]


def test_parse_and_score_resume_sandbox(
    client: TestClient,
    db_session: Session,
    test_job: Job,
    auth_headers: dict[str, str],
) -> None:
    """Verify parsing and scoring candidates in sandbox mode."""
    cand = Candidate(
        job_id=test_job.id,
        name="Alice",
        email="alice@example.com",
        phone="111-222-3333",
        skills="Python",
        experience="3 years",
        education="B.S.",
        status=CandidateStatus.ACTIVE,
        parsed_resume="Candidate: Jane Doe\nEmail: jane.doe@example.com\nPhone: 123-456-7890\nSkills: Python, FastAPI\nEducation: B.S.",
    )
    db_session.add(cand)
    db_session.commit()

    response = client.post(
        f"/api/v1/candidates/{cand.id}/parse",
        headers=auth_headers,
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["name"] == "Candidate: Jane Doe"
    assert res_data["email"] == "jane.doe@example.com"
    assert res_data["parsed_at"] is not None

    response = client.post(
        f"/api/v1/candidates/{cand.id}/fit-score",
        headers=auth_headers,
    )
    assert response.status_code == 200
    score_data = response.json()
    assert score_data["fit_score"] is not None
    assert score_data["fit_reason"] is not None
