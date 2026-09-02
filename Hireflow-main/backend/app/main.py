"""FastAPI application factory.

Creates and configures the FastAPI application with all middleware,
exception handlers, and routers.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.config import get_settings
from app.core.exceptions import BaseAPIException, global_exception_handler
from app.core.logging import get_logger, setup_logging
from app.middleware.error_handling import ErrorHandlingMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware
from app.middleware.request_timing import RequestTimingMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Application lifespan context manager.

    Handles startup and shutdown events.
    """
    setup_logging()
    settings = get_settings()
    logger.info(
        "Starting %s v%s",
        settings.APP_NAME,
        settings.APP_VERSION,
    )
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Fully configured FastAPI instance.
    """
    settings = get_settings()

    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Recruiter Management System — Manage jobs, candidates, "
            "resume parsing, and AI-powered fit scoring."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ---- CORS ----
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---- Custom Middleware ----
    # Note: Middleware is executed in reverse registration order.
    # ErrorHandling → RequestLogging → RequestTiming → Handler
    application.add_middleware(RequestTimingMiddleware)
    application.add_middleware(RequestLoggingMiddleware)
    application.add_middleware(ErrorHandlingMiddleware)
    application.add_middleware(SecurityHeadersMiddleware)

    # ---- Exception Handlers ----
    application.add_exception_handler(BaseAPIException, global_exception_handler)

    # ---- Routers ----
    application.include_router(v1_router)

    return application


app = create_app()
