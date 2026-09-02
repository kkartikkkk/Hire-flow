"""Job service — business logic layer.

Handles job CRUD operations, ownership validation, status management,
search, filtering, and pagination. All database access is delegated
to JobRepository.
"""

import uuid

from app.core.exceptions import AuthorizationException, NotFoundException, ValidationException
from app.core.logging import get_logger
from app.models.job import Job, JobStatus
from app.repositories.job_repository import JobRepository
from app.schemas.job import JobCreate, JobUpdate

logger = get_logger(__name__)


class JobService:
    """Business logic for job management operations.

    All database access is delegated to the injected repository.
    This service handles:
    - Job CRUD with ownership enforcement
    - Status transitions (close)
    - Filtered, paginated listing
    """

    def __init__(self, repository: JobRepository) -> None:
        self.repository = repository

    def create_job(self, recruiter_id: uuid.UUID, data: JobCreate) -> Job:
        """Create a new job posting for the authenticated recruiter.

        Args:
            recruiter_id: The UUID of the authenticated recruiter.
            data: Validated job creation data.

        Returns:
            The newly created Job instance.
        """
        job = self.repository.create_job(
            recruiter_id=recruiter_id,
            title=data.title,
            description=data.description,
            required_skills=data.required_skills,
            experience_required=data.experience_required,
            location=data.location,
            employment_type=data.employment_type,
            salary_range=data.salary_range,
        )
        logger.info("Job created: id=%s recruiter=%s title=%s", job.id, recruiter_id, job.title)
        return job

    def get_job(self, job_id: uuid.UUID, recruiter_id: uuid.UUID) -> Job:
        """Retrieve a single job, enforcing ownership.

        Args:
            job_id: The UUID of the job.
            recruiter_id: The UUID of the authenticated recruiter.

        Returns:
            The Job instance.

        Raises:
            NotFoundException: If the job does not exist.
            AuthorizationException: If the recruiter does not own the job.
        """
        job = self._get_job_or_404(job_id)
        self._enforce_ownership(job, recruiter_id)
        return job

    def update_job(
        self,
        job_id: uuid.UUID,
        recruiter_id: uuid.UUID,
        data: JobUpdate,
    ) -> Job:
        """Update a job posting, enforcing ownership and status rules.

        Args:
            job_id: The UUID of the job to update.
            recruiter_id: The UUID of the authenticated recruiter.
            data: Validated update data (partial).

        Returns:
            The updated Job instance.

        Raises:
            NotFoundException: If the job does not exist.
            AuthorizationException: If the recruiter does not own the job.
            ValidationException: If the job is CLOSED.
        """
        job = self._get_job_or_404(job_id)
        self._enforce_ownership(job, recruiter_id)

        if job.status == JobStatus.CLOSED:
            raise ValidationException(detail="Cannot edit a closed job")

        update_data = data.model_dump(exclude_unset=True)
        job = self.repository.update_job(job, update_data)
        logger.info("Job updated: id=%s", job_id)
        return job

    def delete_job(self, job_id: uuid.UUID, recruiter_id: uuid.UUID) -> None:
        """Delete a job posting, enforcing ownership.

        Args:
            job_id: The UUID of the job to delete.
            recruiter_id: The UUID of the authenticated recruiter.

        Raises:
            NotFoundException: If the job does not exist.
            AuthorizationException: If the recruiter does not own the job.
        """
        job = self._get_job_or_404(job_id)
        self._enforce_ownership(job, recruiter_id)
        self.repository.delete_job(job)
        logger.info("Job deleted: id=%s recruiter=%s", job_id, recruiter_id)

    def close_job(self, job_id: uuid.UUID, recruiter_id: uuid.UUID) -> Job:
        """Close a job posting, enforcing ownership.

        Args:
            job_id: The UUID of the job to close.
            recruiter_id: The UUID of the authenticated recruiter.

        Returns:
            The updated Job instance with CLOSED status.

        Raises:
            NotFoundException: If the job does not exist.
            AuthorizationException: If the recruiter does not own the job.
            ValidationException: If the job is already closed.
        """
        job = self._get_job_or_404(job_id)
        self._enforce_ownership(job, recruiter_id)

        if job.status == JobStatus.CLOSED:
            raise ValidationException(detail="Job is already closed")

        job = self.repository.update_job(job, {"status": JobStatus.CLOSED})
        logger.info("Job closed: id=%s recruiter=%s", job_id, recruiter_id)
        return job

    def list_jobs(
        self,
        recruiter_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        location: str | None = None,
        employment_type: str | None = None,
        search: str | None = None,
    ) -> dict:
        """Retrieve a filtered, paginated list of the recruiter's jobs.

        Args:
            recruiter_id: The UUID of the authenticated recruiter.
            page: Page number (1-indexed).
            page_size: Items per page.
            status: Optional status filter.
            location: Optional location filter.
            employment_type: Optional employment type filter.
            search: Optional search term.

        Returns:
            Paginated result dictionary.
        """
        return self.repository.find_by_recruiter_paginated(
            recruiter_id=recruiter_id,
            page=page,
            page_size=page_size,
            status=status,
            location=location,
            employment_type=employment_type,
            search=search,
        )

    def _get_job_or_404(self, job_id: uuid.UUID) -> Job:
        """Retrieve a job by ID or raise 404.

        Args:
            job_id: The UUID to look up.

        Returns:
            The Job instance.

        Raises:
            NotFoundException: If no job with the given ID exists.
        """
        job = self.repository.find_by_id(job_id)
        if job is None:
            raise NotFoundException(detail="Job not found")
        return job

    @staticmethod
    def _enforce_ownership(job: Job, recruiter_id: uuid.UUID) -> None:
        """Verify that the job belongs to the given recruiter.

        Args:
            job: The job to check.
            recruiter_id: The expected owner UUID.

        Raises:
            AuthorizationException: If the recruiter does not own the job.
        """
        if job.recruiter_id != recruiter_id:
            raise AuthorizationException(detail="You do not have access to this job")
