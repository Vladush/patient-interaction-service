from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.database import get_session
from app.main import app

# Use in-memory SQLite for tests.
# StaticPool is important for in-memory SQLite to share connection across threads.
sqlite_url = "sqlite://"
engine = create_engine(
    sqlite_url, connect_args={"check_same_thread": False}, poolclass=StaticPool
)


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    """
    Creates a fresh database for each test.
    """
    SQLModel.metadata.create_all(engine)

    # Seed default outcomes for testing
    from app.models.outcome import Outcome

    with Session(engine) as seed_session:
        defaults = ["Healthy", "Monitor", "Critical"]
        for code in defaults:
            seed_session.add(Outcome(code=code, description="Test Default"))
        seed_session.commit()

    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """
    Creates a TestClient that uses the override database session.
    """

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    yield TestClient(app)
    app.dependency_overrides.clear()
