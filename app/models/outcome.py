from typing import Optional

from sqlmodel import Field, SQLModel


class Outcome(SQLModel, table=True):
    """
    Configurable Outcome reference data.
    Acts as the source of truth for valid Interaction outcomes.
    """
    code: str = Field(primary_key=True)
    description: Optional[str] = None
