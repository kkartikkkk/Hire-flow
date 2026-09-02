"""Resume parser service.

Coordinates with the injected AI provider to extract structured
candidate details from raw resume text content.
"""

from typing import Any

from app.ai.provider import AIProvider
from app.core.logging import get_logger

logger = get_logger(__name__)


class ResumeParserService:
    """Orchestrates resume parsing using the AI provider."""

    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    async def parse_resume(self, content: str) -> dict[str, Any]:
        """Parse raw resume text content.

        Args:
            content: Raw extracted text of the resume.

        Returns:
            Dict containing name, email, phone, skills, experience, and education.
        """
        logger.info("Parsing resume content via AI parser service")
        parsed = await self.provider.parse_resume(content)
        return parsed
