from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.models import Outcome

router = APIRouter()


@router.get("/", response_model=List[Outcome])
def list_outcomes(session: Session = Depends(get_session)):
    """List all configured outcomes."""
    # TODO: Cache this result (Redis/Memcached) as outcomes change rarely.
    return session.exec(select(Outcome)).all()


@router.post("/", response_model=Outcome, status_code=status.HTTP_201_CREATED)
def create_outcome(outcome: Outcome, session: Session = Depends(get_session)):
    """Create a new valid outcome."""
    if session.get(Outcome, outcome.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Outcome '{outcome.code}' already exists.",
        )
    session.add(outcome)
    session.commit()
    session.refresh(outcome)
    return outcome


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_outcome(code: str, session: Session = Depends(get_session)):
    """
    Remove an outcome from the valid list.
    Existing interactions with this outcome are preserved (soft validation).
    """
    outcome = session.get(Outcome, code)
    if not outcome:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Outcome not found"
        )
    session.delete(outcome)
    session.commit()


@router.put("/{code}", response_model=Outcome)
def update_outcome(
    code: str,
    outcome_update: Outcome,
    session: Session = Depends(get_session),
):
    """
    Update outcome description.
    Note: The code (ID) cannot be changed via this endpoint.
    """
    db_outcome = session.get(Outcome, code)
    if not db_outcome:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Outcome not found"
        )

    if outcome_update.description is not None:
        db_outcome.description = outcome_update.description

    session.add(db_outcome)
    session.commit()
    session.refresh(db_outcome)
    return db_outcome
