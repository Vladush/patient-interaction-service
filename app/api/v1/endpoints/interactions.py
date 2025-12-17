import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.models import Interaction, Outcome, Patient
from app.schemas.interaction import InteractionCreate, InteractionRead, InteractionUpdate

router = APIRouter()


@router.post("/", response_model=InteractionRead, status_code=status.HTTP_201_CREATED)
def create_interaction(
    interaction: InteractionCreate, session: Session = Depends(get_session)
):
    """
    Document a patient interaction.
    """

    patient = session.get(Patient, interaction.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {interaction.patient_id} not found",
        )
        
    # TODO: Move this validation logic to a service layer
    _validate_outcome(session, interaction.outcome)

    db_interaction = Interaction.model_validate(interaction)
    session.add(db_interaction)
    session.commit()
    session.refresh(db_interaction)
    return db_interaction


@router.get("/", response_model=List[InteractionRead])
def read_interactions(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = 100,
    patient_id: uuid.UUID | None = None,
    outcome: str | None = None,
):
    """
    Retrieve interactions with optional filtering.
    """
    statement = select(Interaction).order_by(Interaction.timestamp.desc())

    if patient_id:
        statement = statement.where(Interaction.patient_id == patient_id)
    
    if outcome:
        statement = statement.where(Interaction.outcome == outcome)

    return session.exec(statement.offset(offset).limit(limit)).all()


@router.put("/{interaction_id}", response_model=InteractionRead)
def update_interaction(
    interaction_id: uuid.UUID,
    interaction_update: InteractionUpdate,
    session: Session = Depends(get_session),
):
    """
    Update interaction details (notes, outcome).
    """
    db_interaction = session.get(Interaction, interaction_id)
    if not db_interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found"
        )

    # Validate Outcome if present
    if interaction_update.outcome:
        _validate_outcome(session, interaction_update.outcome)

    interaction_data = interaction_update.model_dump(exclude_unset=True)
    for key, value in interaction_data.items():
        setattr(db_interaction, key, value)

    session.add(db_interaction)
    session.commit()
    session.refresh(db_interaction)
    return db_interaction


@router.delete("/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interaction(
    interaction_id: uuid.UUID, session: Session = Depends(get_session)
):
    """
    Delete a specific interaction.
    """
    interaction = session.get(Interaction, interaction_id)
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found"
        )
    session.delete(interaction)
    session.commit()


def _validate_outcome(session: Session, outcome_code: str):
    """
    Helper to validate that an outcome configuration exists.
    """
    if not session.get(Outcome, outcome_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid outcome '{outcome_code}'. Please configure it first.",
        )
