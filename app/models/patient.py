import uuid
from datetime import date
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .interaction import Interaction


class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"
    UNKNOWN = "Unknown"


class PatientBase(SQLModel):
    first_name: str = Field(index=True)
    last_name: str = Field(index=True)
    date_of_birth: date
    gender: Gender


class Patient(PatientBase, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    # Relationship to interactions
    interactions: List["Interaction"] = Relationship(
        back_populates="patient",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
