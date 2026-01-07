import uuid
from datetime import datetime

from app.models.interaction import InteractionBase


class InteractionCreate(InteractionBase):
    """Schema for creating an interaction. Requires patient_id."""

    patient_id: uuid.UUID


class InteractionUpdate(InteractionBase):
    """Schema for updating an interaction."""

    notes: str | None = None
    outcome: str | None = None


class InteractionRead(InteractionBase):
    """Schema for reading an interaction. Includes system-generated fields."""

    id: uuid.UUID
    timestamp: datetime
    patient_id: uuid.UUID
