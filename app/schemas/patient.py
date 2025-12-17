import uuid
from datetime import date

from app.models.patient import Gender, PatientBase


class PatientCreate(PatientBase):
    """Schema for creating a patient."""
    pass


class PatientUpdate(PatientBase):
    """Schema for updating a patient."""
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    gender: Gender | None = None


class PatientRead(PatientBase):
    """Schema for reading a patient."""
    id: uuid.UUID
