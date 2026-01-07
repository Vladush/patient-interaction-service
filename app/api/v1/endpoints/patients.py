import uuid
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.models import Gender, Patient
from app.schemas.patient import PatientCreate, PatientRead, PatientUpdate

router = APIRouter()


@router.post("/", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
def create_patient(patient: PatientCreate, session: Session = Depends(get_session)):
    db_patient = Patient.model_validate(patient)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient


@router.get("/", response_model=List[PatientRead])
def read_patients(
    session: Session = Depends(get_session),
    first_name: str | None = None,
    last_name: str | None = None,
    date_of_birth: date | None = None,
    gender: Gender | None = None,
    offset: int = 0,
    limit: int = 100,
):
    # TODO: Index if search volume increases

    query = select(Patient)
    if first_name:
        query = query.where(Patient.first_name == first_name)
    if last_name:
        query = query.where(Patient.last_name == last_name)
    if date_of_birth:
        query = query.where(Patient.date_of_birth == date_of_birth)
    if gender:
        query = query.where(Patient.gender == gender)

    return session.exec(query.offset(offset).limit(limit)).all()


@router.put("/{patient_id}", response_model=PatientRead)
def update_patient(
    patient_id: uuid.UUID,
    patient_update: PatientUpdate,
    session: Session = Depends(get_session),
):
    db_patient = session.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )

    patient_data = patient_update.model_dump(exclude_unset=True)
    for key, value in patient_data.items():
        setattr(db_patient, key, value)

    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)
    return db_patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: uuid.UUID, session: Session = Depends(get_session)):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )
    session.delete(patient)
    session.commit()
