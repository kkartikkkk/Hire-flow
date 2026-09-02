"""Fit score service.

Coordinates with the injected AI provider to calculate job-candidate
fit scores based on parsed profile details and job requirements.
"""

from typing import Any

from app.ai.provider import AIProvider
from app.core.logging import get_logger

logger = get_logger(__name__)


class FitScoreService:
    """Orchestrates candidate fit scoring using the AI provider."""

    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    async def calculate_fit_score(
        self,
        resume_data: dict[str, Any],
        job_requirements: dict[str, Any],
    ) -> dict[str, Any]:
        """Assess overall job fit.

        Args:
            resume_data: Parsed resume details.
            job_requirements: Job requirements (title, required_skills, etc.).

        Returns:
            Dict containing score (0-100), explanation, strengths, and gaps.
        """
        logger.info("Computing candidate-job fit score via AI fit scoring service")
        result = await self.provider.calculate_fit_score(resume_data, job_requirements)
        return result
