"""AI provider abstract interface.

All AI providers must implement this interface.
This allows swapping providers without changing application code.
"""

from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    """Abstract base class for AI providers.

    Any AI provider (Grok, OpenAI, Anthropic, etc.) must implement
    these methods to be used by the application's AI services.
    """

    @abstractmethod
    async def parse_resume(self, content: str) -> dict[str, Any]:
        """Parse resume content and extract structured data.

        Args:
            content: Raw text content of the resume.

        Returns:
            Dictionary containing structured resume data including
            name, email, skills, experience, education, etc.
        """
        ...

    @abstractmethod
    async def calculate_fit_score(
        self,
        resume_data: dict[str, Any],
        job_requirements: dict[str, Any],
    ) -> dict[str, Any]:
        """Calculate how well a candidate fits a job.

        Args:
            resume_data: Structured resume data from parse_resume.
            job_requirements: Structured job requirements.

        Returns:
            Dictionary containing fit score (0-100), reasoning,
            strengths, and gaps.
        """
        ...
