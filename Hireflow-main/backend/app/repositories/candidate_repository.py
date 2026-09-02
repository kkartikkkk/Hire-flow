"""Candidate repository — data access layer.

Provides database operations for Candidate entities including
CRUD, filtering, search, and pagination.
Contains only database logic.
"""

import math
import uuid
from datetime import date
from typing import Any

from sqlalchemy import or_, cast, Date
from sqlalchemy.orm import Session

from app.models.candidate import Candidate, CandidateStatus
from app.models.job import Job
from app.repositories.base import BaseRepository


class CandidateRepository(BaseRepository[Candidate]):
    """Data access layer for Candidate entities.

    Extends BaseRepository with candidate-specific queries.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(model=Candidate, db=db)

    def find_by_id(self, candidate_id: uuid.UUID) -> Candidate | None:
        """Retrieve a single candidate by UUID.

        Args:
            candidate_id: UUID of candidate.

        Returns:
            Candidate or None.
        """
        return self.db.query(Candidate).filter(Candidate.id == candidate_id).first()

    def find_by_job(self, job_id: uuid.UUID) -> list[Candidate]:
        """Retrieve all candidates applying to a job.

        Args:
            job_id: UUID of the job.

        Returns:
            List of candidates.
        """
        return self.db.query(Candidate).filter(Candidate.job_id == job_id).all()

    def find_by_recruiter_paginated(
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
        """Retrieve, filter, and paginate candidates belonging to a recruiter's jobs.

        Args:
            recruiter_id: Recruiter UUID to enforce ownership.
            page: Page number (1-indexed).
            page_size: Number of items per page.
            status: Filter by candidate status.
            job_id: Filter by job UUID.
            experience: Filter by experience contains.
            created_date: Filter by exact creation date.
            search: Search in name, email, phone, and skills.

        Returns:
            Dict containing pagination metadata and items.
        """
        # Join with Job to ensure the job belongs to the recruiter
        query = (
            self.db.query(Candidate)
            .join(Job, Candidate.job_id == Job.id)
            .filter(Job.recruiter_id == recruiter_id)
        )

        # Apply filters
        if status:
            query = query.filter(Candidate.status == status)
        if job_id:
            query = query.filter(Candidate.job_id == job_id)
        if experience:
            query = query.filter(Candidate.experience.ilike(f"%{experience}%"))
        if created_date:
            query = query.filter(cast(Candidate.created_at, Date) == created_date)

        # Apply search
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Candidate.name.ilike(search_term),
                    Candidate.email.ilike(search_term),
                    Candidate.phone.ilike(search_term),
                    Candidate.skills.ilike(search_term),
                )
            )

        # Pagination calculations
        total = query.count()
        total_pages = max(1, math.ceil(total / page_size))
        offset = (page - 1) * page_size

        items = (
            query.order_by(Candidate.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        }
