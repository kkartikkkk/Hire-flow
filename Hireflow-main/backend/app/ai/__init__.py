"""AI layer package.

Provides a provider abstraction for AI operations.
The provider is replaceable without changing application code.
"""

from app.ai.factory import get_ai_provider
from app.ai.provider import AIProvider

__all__ = ["AIProvider", "get_ai_provider"]
