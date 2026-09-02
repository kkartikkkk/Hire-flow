"""Candidate service — business logic layer.

Handles candidate CRUD, resume uploads, text extraction, AI parsing,
AI fit scoring, search, filtering, and recruiter ownership validation.
"""

import json
import uuid
from datetime import date, datetime
from typing import Any
from fastapi import UploadFile

from app.core.exceptions import AuthorizationException, NotFoundException, ValidationException
from app.core.logging import get_logger
from app.models.candidate import Candidate, CandidateStatus
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.job_repository import JobRepository
from app.schemas.candidate import CandidateCreate, CandidateUpdate
from app.services.resume_parser_service import ResumeParserService
from app.services.fit_score_service import FitScoreService
from app.utils.file_utils import (
    save_upload_file,
    extract_text_from_pdf,
    extract_text_from_docx,
)

logger = get_logger(__name__)


class CandidateService:
    """Business logic for candidate management and resume AI pipelines.

    Enforces ownership validation checks at every boundary.
    """

    def __init__(
        self,
        repository: CandidateRepository,
        job_repository: JobRepository,
        parser_service: ResumeParserService,
        score_service: FitScoreService,
    ) -> None:
        self.repository = repository
        self.job_repository = job_repository
        self.parser_service = parser_service
        self.score_service = score_service

    def create_candidate(self, recruiter_id: uuid.UUID, data: CandidateCreate) -> Candidate:
        """Create a candidate application after validating job ownership."""
        job = self.job_repository.find_by_id(data.job_id)
        if not job:
            raise NotFoundException("Job not found")
        if job.recruiter_id != recruiter_id:
            raise AuthorizationException("You do not have access to this job")

        candidate = Candidate(
            job_id=data.job_id,
            name=data.name,
            email=data.email,
            phone=data.phone,
            resume_filename=data.resume_filename,
            skills=data.skills,
            experience=data.experience,
            education=data.education,
            fit_score=data.fit_score,
            fit_reason=data.fit_reason,
            status=data.status,
            notes=data.notes,
        )
        saved = self.repository.create(candidate)
        logger.info("Candidate created: id=%s name=%s job_id=%s", saved.id, saved.name, saved.job_id)
        return saved

    def get_candidate(self, recruiter_id: uuid.UUID, candidate_id: uuid.UUID) -> Candidate:
        """Retrieve a candidate after verifying recruiter ownership."""
        candidate = self._get_candidate_or_404(candidate_id)
        self._enforce_ownership(candidate, recruiter_id)
        return candidate

    def update_candidate(
        self,
        recruiter_id: uuid.UUID,
        candidate_id: uuid.UUID,
        data: CandidateUpdate,
    ) -> Candidate:
        """Update candidate details, verifying ownership."""
        candidate = self._get_candidate_or_404(candidate_id)
        self._enforce_ownership(candidate, recruiter_id)

        update_dict = data.model_dump(exclude_unset=True)
        updated = self.repository.update(candidate, update_dict)
        logger.info("Candidate updated: id=%s", candidate_id)
        return updated

    def delete_candidate(self, recruiter_id: uuid.UUID, candidate_id: uuid.UUID) -> None:
        """Delete candidate application, verifying ownership."""
        candidate = self._get_candidate_or_404(candidate_id)
        self._enforce_ownership(candidate, recruiter_id)

        self.repository.delete(candidate)
        logger.info("Candidate deleted: id=%s", candidate_id)

    def list_candidates(
        self,
        recruiter_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        status: CandidateStatus | None = None,
        job_id: uuid.UUID | None = None,
        experience: str | None = None,
        created_date: date | None = None,
        search: str | None = None,
    ) -> dict[str, Any]:
        """List, search, filter, and paginate recruiter's candidates."""
        return self.repository.find_by_recruiter_paginated(
            recruiter_id=recruiter_id,
            page=page,
            page_size=page_size,
            status=status,
            job_id=job_id,
            experience=experience,
            created_date=created_date,
            search=search,
        )

    async def save_resume_upload(
        self,
        candidate_id: uuid.UUID,
        file: UploadFile,
        recruiter_id: uuid.UUID,
    ) -> Candidate:
        """Save resume document file, extract text, and update candidate profile."""
        candidate = self._get_candidate_or_404(candidate_id)
        self._enforce_ownership(candidate, recruiter_id)

        # 1. Save uploaded file securely
        saved_path = await save_upload_file(file)

        # 2. Extract plain text based on extension
        suffix = saved_path.suffix.lower()
        try:
            if suffix == ".pdf":
                extracted_text = extract_text_from_pdf(saved_path)
            elif suffix == ".docx":
                extracted_text = extract_text_from_docx(saved_path)
            else:
                raise ValidationException("Unsupported file format.")
        except Exception as exc:
            # Cleanup saved file if text extraction fails
            saved_path.unlink(missing_ok=True)
            logger.error("Failed text extraction for %s: %s", saved_path.name, exc)
            raise ValidationException("Failed to extract plain text from resume document.") from exc

        # 3. Update candidate record
        update_data = {
            "resume_filename": file.filename,
            "parsed_resume": extracted_text,
        }
        updated = self.repository.update(candidate, update_data)
        logger.info("Resume uploaded and text extracted: candidate_id=%s file=%s", candidate_id, file.filename)
        return updated

    async def parse_candidate_resume(
        self,
        candidate_id: uuid.UUID,
        recruiter_id: uuid.UUID,
    ) -> Candidate:
        """Invoke AI parser service to extract details from candidate's uploaded resume text."""
        candidate = self._get_candidate_or_404(candidate_id)
        self._enforce_ownership(candidate, recruiter_id)

        if not candidate.parsed_resume:
            raise ValidationException("No resume text extracted. Please upload a resume document first.")

        try:
            parsed_data = await self.parser_service.parse_resume(candidate.parsed_resume)
            
            # Helper to join list values to clean strings
            def list_to_str(val: Any) -> str:
                if isinstance(val, list):
                    return "\n".join([str(item) for item in val])
                return str(val or "")

            update_data = {
                "name": parsed_data.get("name") or candidate.name,
                "email": parsed_data.get("email") or candidate.email,
                "phone": parsed_data.get("phone") or candidate.phone,
                "skills": list_to_str(parsed_data.get("skills")),
                "experience": list_to_str(parsed_data.get("experience")),
                "education": list_to_str(parsed_data.get("education")),
                "parsed_at": datetime.now(),
            }
            # Add projects/certifications to notes if recruiter notes is empty
            extra_info = []
            if parsed_data.get("projects"):
                extra_info.append(f"Projects:\n{list_to_str(parsed_data.get('projects'))}")
            if parsed_data.get("certifications"):
                extra_info.append(f"Certifications:\n{list_to_str(parsed_data.get('certifications'))}")
            
            if extra_info:
                current_notes = candidate.notes or ""
                update_data["notes"] = f"{current_notes}\n\n" + "\n\n".join(extra_info) if current_notes else "\n\n".join(extra_info)

            updated = self.repository.update(candidate, update_data)
            logger.info("Resume parsed via Grok AI for candidate_id=%s", candidate_id)
            return updated
        except Exception as exc:
            logger.error("AI parsing failure for candidate_id=%s: %s", candidate_id, exc)
            raise

    async def calculate_candidate_fit_score(
        self,
        candidate_id: uuid.UUID,
        recruiter_id: uuid.UUID,
    ) -> Candidate:
        """Invoke AI fit scoring service to assess candidate match against job requirements."""
        candidate = self._get_candidate_or_404(candidate_id)
        self._enforce_ownership(candidate, recruiter_id)

        job = self.job_repository.find_by_id(candidate.job_id)
        if not job:
            raise NotFoundException("Associated job opening not found.")

        # Construct payloads
        resume_data = {
            "name": candidate.name,
            "skills": [s.strip() for s in candidate.skills.split("\n") if s.strip()],
            "experience": [e.strip() for e in candidate.experience.split("\n") if e.strip()],
            "education": [ed.strip() for ed in candidate.education.split("\n") if ed.strip()],
        }

        job_requirements = {
            "title": job.title,
            "description": job.description,
            "required_skills": job.required_skills,
            "experience_required": job.experience_required,
            "location": job.location,
            "employment_type": job.employment_type,
        }

        try:
            fit_result = await self.score_service.calculate_fit_score(resume_data, job_requirements)
            
            update_data = {
                "fit_score": fit_result.get("score") or 0,
                "fit_reason": json.dumps({
                    "strengths": fit_result.get("strengths") or [],
                    "missing_skills": fit_result.get("missing_skills") or [],
                    "recommendation": fit_result.get("recommendation") or "",
                    "summary": fit_result.get("summary") or "",
                }),
            }
            updated = self.repository.update(candidate, update_data)
            logger.info("Candidate fit score calculated for candidate_id=%s: %d", candidate_id, updated.fit_score or 0)
            return updated
        except Exception as exc:
            logger.error("AI fit scoring failure for candidate_id=%s: %s", candidate_id, exc)
            raise

    async def create_candidate_from_resume(
        self,
        recruiter_id: uuid.UUID,
        job_id: uuid.UUID,
        file: UploadFile,
    ) -> Candidate:
        """Create a candidate directly from a resume upload by automatically parsing details."""
        job = self.job_repository.find_by_id(job_id)
        if not job:
            raise NotFoundException("Job not found")
        if job.recruiter_id != recruiter_id:
            raise AuthorizationException("You do not have access to this job")

        # Save and validate the uploaded resume file
        file_path = await save_upload_file(file)
        unique_filename = file_path.name

        # Extract raw text
        if unique_filename.lower().endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        else:
            text = extract_text_from_docx(file_path)

        # Parse text using AI
        parsed_data = await self.parser_service.parse_resume(text)

        # Helper to join list values to clean strings
        def list_to_str(val: Any) -> str:
            if isinstance(val, list):
                return "\n".join([str(item) for item in val])
            return str(val or "")

        skills_str = ", ".join([str(s) for s in parsed_data.get("skills", [])]) if isinstance(parsed_data.get("skills"), list) else str(parsed_data.get("skills") or "")
        experience_str = list_to_str(parsed_data.get("experience"))
        education_str = list_to_str(parsed_data.get("education"))

        candidate = Candidate(
            job_id=job_id,
            name=parsed_data.get("name") or "Parsed Applicant",
            email=parsed_data.get("email") or "parsed@example.com",
            phone=parsed_data.get("phone") or "000-000-0000",
            resume_filename=unique_filename,
            skills=skills_str,
            experience=experience_str,
            education=education_str,
            status=CandidateStatus.ACTIVE,
            parsed_resume=text,
            parsed_at=datetime.utcnow(),
        )

        candidate = self.repository.create(candidate)
        logger.info("Candidate quick-created from resume file: id=%s name=%s", candidate.id, candidate.name)

        # Automatically calculate the fit score
        try:
            resume_data = {
                "name": candidate.name,
                "skills": parsed_data.get("skills") or [],
                "experience": parsed_data.get("experience") or [],
                "education": parsed_data.get("education") or [],
            }
            job_requirements = {
                "title": job.title,
                "description": job.description,
                "required_skills": job.required_skills,
                "experience_required": job.experience_required,
                "location": job.location,
                "employment_type": job.employment_type,
            }
            fit_result = await self.score_service.calculate_fit_score(resume_data, job_requirements)
            
            update_data = {
                "fit_score": fit_result.get("score") or 0,
                "fit_reason": json.dumps({
                    "strengths": fit_result.get("strengths") or [],
                    "missing_skills": fit_result.get("missing_skills") or [],
                    "recommendation": fit_result.get("recommendation") or "",
                    "summary": fit_result.get("summary") or "",
                }),
            }
            self.repository.update(candidate, update_data)
        except Exception as exc:
            logger.error("Automatic fit scoring failed for candidate %s: %s", candidate.id, exc)

        return candidate

    def _get_candidate_or_404(self, candidate_id: uuid.UUID) -> Candidate:
        """Fetch candidate or raise 404."""
        candidate = self.repository.find_by_id(candidate_id)
        if not candidate:
            raise NotFoundException("Candidate not found")
        return candidate

    def _enforce_ownership(self, candidate: Candidate, recruiter_id: uuid.UUID) -> None:
        """Enforce job-candidate ownership hierarchy."""
        job = self.job_repository.find_by_id(candidate.job_id)
        if not job or job.recruiter_id != recruiter_id:
            raise AuthorizationException("You do not have access to this candidate")
