"""Main API v1 router.

Aggregates all sub-routers under the /api/v1 prefix.
"""

from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.auth.routes import router as auth_router
from app.api.v1.jobs.routes import router as jobs_router
from app.api.v1.candidates.routes import router as candidates_router
from app.api.v1.dashboard.routes import router as dashboard_router

router = APIRouter(prefix="/api/v1")

router.include_router(health_router)
router.include_router(auth_router)
router.include_router(jobs_router)
router.include_router(candidates_router)
router.include_router(dashboard_router)
