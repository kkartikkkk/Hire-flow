import os
import sys

# Set database URL to in-memory SQLite before importing application modules
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Mock password hashing functions to bypass passlib/bcrypt incompatibility on host Python 3.14
def mock_hash_password(plain: str) -> str:
    return f"mocked_{plain}"

def mock_verify_password(plain: str, hashed: str) -> bool:
    return hashed == f"mocked_{plain}"

# Pre-import and patch the security password module
import app.core.security.password
app.core.security.password.hash_password = mock_hash_password
app.core.security.password.verify_password = mock_verify_password

from collections.abc import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_settings
from app.core.security.jwt import create_access_token
from app.core.security.password import hash_password
from app.database.base import Base
from app.dependencies.database import get_db
from app.main import app as fastapi_app
from app.models.recruiter import Recruiter
from app.models.job import Job, JobStatus
from app.models.candidate import Candidate, CandidateStatus

# Use an in-memory SQLite database for fast, isolated tests
SQLALCHEMY_DATABASE_URL = "sqlite:///file:testdb?mode=memory&cache=shared"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False, "uri": True},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Monkeypatch the database session factory so the application code uses the test session factory
import app.database.session
app.database.session.SessionLocal = TestingSessionLocal

import app.services.candidate_service
app.services.candidate_service.SessionLocal = TestingSessionLocal


# Keep a connection open for the entire session to prevent SQLite from releasing the in-memory database
persistent_connection = None


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> Generator[None, None, None]:
    """Create all database tables once for the test session and keep database alive."""
    global persistent_connection
    persistent_connection = engine.connect()
    
    # Import all models to ensure they register on Base
    import app.models  # noqa: F401
    
    print("Base metadata tables found:", list(Base.metadata.tables.keys()))
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    yield
    
    persistent_connection.close()


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provide a clean, isolated database transaction for each test case."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(autouse=True)
def override_db_dependency(db_session: Session) -> Generator[None, None, None]:
    """Override the get_db FastAPI dependency to use the isolated test session."""
    def _get_db_override() -> Generator[Session, None, None]:
        yield db_session

    fastapi_app.dependency_overrides[get_db] = _get_db_override
    yield
    fastapi_app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def client() -> TestClient:
    """FastAPI TestClient instance."""
    return TestClient(fastapi_app)


@pytest.fixture
def test_recruiter(db_session: Session) -> Recruiter:
    """Create a default test recruiter."""
    import uuid
    recruiter = Recruiter(
        name="Test Recruiter",
        email=f"recruiter_{uuid.uuid4()}@example.com",
        password_hash=hash_password("password123"),
    )
    db_session.add(recruiter)
    db_session.commit()
    db_session.refresh(recruiter)
    return recruiter


@pytest.fixture
def auth_headers(test_recruiter: Recruiter) -> dict[str, str]:
    """Generate authentication headers for the test recruiter."""
    token = create_access_token(data={"sub": str(test_recruiter.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_job(db_session: Session, test_recruiter: Recruiter) -> Job:
    """Create a default test job posting owned by test_recruiter."""
    job = Job(
        recruiter_id=test_recruiter.id,
        title="Software Engineer",
        description="Write high-quality clean Python code.",
        required_skills="Python, FastAPI, Docker",
        experience_required=3,
        location="Remote",
        employment_type="Full-time",
        status=JobStatus.OPEN,
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job
