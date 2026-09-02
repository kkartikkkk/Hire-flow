"""AI provider factory.

Returns the appropriate AI provider instance based on configuration.
New providers can be added without modifying application code.
"""

from app.ai.grok_provider import GrokProvider
from app.ai.provider import AIProvider
from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_PROVIDERS: dict[str, type[AIProvider]] = {
    "grok": GrokProvider,
}


def get_ai_provider() -> AIProvider:
    """Create and return the configured AI provider instance.

    Reads AI_PROVIDER from settings and instantiates the matching
    provider class.

    Returns:
        An AIProvider implementation.

    Raises:
        ValueError: If the configured provider is not supported.
    """
    settings = get_settings()
    provider_name = settings.AI_PROVIDER.lower()

    provider_class = _PROVIDERS.get(provider_name)
    if provider_class is None:
        supported = ", ".join(_PROVIDERS.keys())
        raise ValueError(
            f"Unknown AI provider '{provider_name}'. Supported: {supported}"
        )

    logger.info("Creating AI provider: %s", provider_name)
    return provider_class()
