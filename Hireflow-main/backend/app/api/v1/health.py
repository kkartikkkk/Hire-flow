"""Health check endpoints.

Provides liveness and readiness probes for container orchestration
and monitoring systems.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.schemas.common import HealthResponse, ReadinessResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthResponse,
    summary="Liveness check",
    description="Returns healthy if the application is running.",
)
async def health_check() -> HealthResponse:
    """Basic liveness probe — confirms the application process is alive."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Readiness check",
    description="Checks database connectivity and returns readiness status.",
)
def readiness_check(db: Session = Depends(get_db)) -> ReadinessResponse:
    """Readiness probe — confirms the application can serve traffic.

    Verifies database connectivity by executing a simple query.
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    status = "ready" if db_status == "connected" else "not_ready"

    return ReadinessResponse(
        status=status,
        database=db_status,
        timestamp=datetime.now(timezone.utc),
    )
