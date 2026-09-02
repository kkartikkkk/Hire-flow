"""Application configuration using Pydantic Settings.

All environment variables are loaded and validated here.
Never use os.getenv() outside this module.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application configuration.

    All values are loaded from environment variables or a .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ---- Application ----
    APP_NAME: str = "Gappeo Recruiter"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ---- Database ----
    DATABASE_URL: str = "postgresql://gappeo_user:gappeo_password@postgres:5432/gappeo_recruiter"

    # ---- JWT Authentication ----
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30

    # ---- AI Provider ----
    AI_PROVIDER: str = "grok"
    AI_BASE_URL: str = "https://api.x.ai/v1"
    AI_API_KEY: str = ""
    AI_MODEL: str = "openai/gpt-oss-120b"

    # ---- File Upload ----
    UPLOAD_DIRECTORY: str = "./uploads"

    # ---- Logging ----
    LOG_LEVEL: str = "INFO"

    # ---- CORS ----
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS comma-separated string into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def normalized_database_url(self) -> str:
        """SQLAlchemy 1.4+ requires 'postgresql://' instead of 'postgres://'."""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
