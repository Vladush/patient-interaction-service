from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings
from app.models import Outcome

# SQLite specific argument to allow multi-threaded access in Dev
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

# echo=True logs SQL queries to console, useful for debugging during the task
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, echo=settings.DB_ECHO)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency Injection provider for Database Sessions.
    Ensures session is closed after request completes.
    """
    with Session(engine) as session:
        yield session


def init_db() -> None:
    """
    Creates tables based on SQLModel definitions.
    In production, this would be replaced by Alembic migrations.
    """
    # TODO: Switch to Alembic for proper migration management in prod
    SQLModel.metadata.create_all(engine)
    
    # Seed default outcomes
    with Session(engine) as session:
        defaults = ["Healthy", "Monitor", "Critical"]
        for code in defaults:
            if not session.get(Outcome, code):
                session.add(Outcome(code=code, description="System Default"))
        session.commit()
