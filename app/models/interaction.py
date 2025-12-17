import uuid
from datetime import datetime, timezone

from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .patient import Patient


class InteractionBase(SQLModel):


    notes: str
    outcome: str


class Interaction(InteractionBase, table=True):


    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)

    patient_id: uuid.UUID = Field(foreign_key="patient.id", index=True)

    patient: Optional["Patient"] = Relationship(back_populates="interactions")
