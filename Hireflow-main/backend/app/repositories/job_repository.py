"""Job repository — data access layer.

Provides database operations for Job entities including
CRUD, filtering, search, and pagination.
Contains no business logic — only queries.
"""

import math
import uuid

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.job import Job, JobStatus
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository[Job]):
    """Data access layer for Job entities.

    Extends BaseRepository with job-specific queries including
    filtering, search, and paginated listing.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(model=Job, db=db)

    def create_job(
        self,
        recruiter_id: uuid.UUID,
        title: str,
        description: str,
        required_skills: str,
        experience_required: int,
        location: str,
        employment_type: str,
        salary_range: str | None = None,
    ) -> Job:
        """Create a new job posting.

        Args:
            recruiter_id: The owning recruiter's UUID.
            title: Job title.
            description: Full description.
            required_skills: Required skills text.
            experience_required: Minimum years of experience.
            location: Job location.
            employment_type: Type of employment.
            salary_range: Optional salary range.

        Returns:
            The newly created Job instance.
        """
        job = Job(
            recruiter_id=recruiter_id,
            title=title,
            description=description,
            required_skills=required_skills,
            experience_required=experience_required,
            location=location,
            employment_type=employment_type,
            salary_range=salary_range,
        )
        return self.create(job)

    def find_by_id(self, job_id: uuid.UUID) -> Job | None:
        """Find a job by its UUID.

        Args:
            job_id: The UUID to search for.

        Returns:
            The Job instance or None if not found.
        """
        return self.db.query(Job).filter(Job.id == job_id).first()

    def find_by_recruiter_paginated(
        self,
        recruiter_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        location: str | None = None,
        employment_type: str | None = None,
        search: str | None = None,
    ) -> dict:
        """Retrieve a filtered, paginated list of jobs for a recruiter.

        Args:
            recruiter_id: Filter by owning recruiter.
            page: Page number (1-indexed).
            page_size: Number of items per page.
            status: Optional status filter (OPEN/CLOSED).
            location: Optional location filter (case-insensitive contains).
            employment_type: Optional employment type filter.
            search: Optional search term for title, description, skills.

        Returns:
            Dictionary with items, total, page, page_size, total_pages,
            has_next, has_previous.
        """
        query = self.db.query(Job).filter(Job.recruiter_id == recruiter_id)

        # Apply filters
        query = self._apply_filters(query, status, location, employment_type, search)

        # Count total before pagination
        total = query.count()
        total_pages = max(1, math.ceil(total / page_size))

        # Apply pagination
        offset = (page - 1) * page_size
        items = query.order_by(Job.created_at.desc()).offset(offset).limit(page_size).all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        }

    def update_job(self, job: Job, update_data: dict) -> Job:
        """Update job fields with the provided data.

        Only non-None values from update_data are applied.

        Args:
            job: The existing Job instance.
            update_data: Dictionary of field names and new values.

        Returns:
            The updated Job instance.
        """
        filtered = {k: v for k, v in update_data.items() if v is not None}
        if not filtered:
            return job
        return self.update(job, filtered)

    def delete_job(self, job: Job) -> None:
        """Delete a job from the database.

        Args:
            job: The Job instance to delete.
        """
        self.delete(job)

    @staticmethod
    def _apply_filters(
        query,
        status: str | None,
        location: str | None,
        employment_type: str | None,
        search: str | None,
    ):
        """Apply filtering and search conditions to a query.

        Args:
            query: The base SQLAlchemy query.
            status: Status filter value.
            location: Location contains filter.
            employment_type: Employment type filter.
            search: Search term for title/description/skills.

        Returns:
            The filtered query.
        """
        if status:
            query = query.filter(Job.status == status)

        if location:
            query = query.filter(Job.location.ilike(f"%{location}%"))

        if employment_type:
            query = query.filter(Job.employment_type.ilike(f"%{employment_type}%"))

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Job.title.ilike(search_term),
                    Job.description.ilike(search_term),
                    Job.required_skills.ilike(search_term),
                )
            )

        return query
