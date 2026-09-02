"""ORM models package.

All models are imported here so Alembic can discover them via
Base.metadata for migration auto-generation.
"""

from app.models.recruiter import *  # noqa: F401, F403
from app.models.job import *  # noqa: F401, F403
from app.models.candidate import *  # noqa: F401, F403
