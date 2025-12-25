from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Attempt, Problem, Session as SessionModel
from app.schemas import AttemptCreate, AttemptResponse
from app.dependencies import get_session_id, verify_session

router = APIRouter()


@router.post("", response_model=AttemptResponse, status_code=status.HTTP_201_CREATED)
def create_attempt(
    attempt: AttemptCreate,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id)
):
    """
    Store attempt metrics for a problem.
    Requires a valid session ID in the X-Session-ID header.
    """
    # Verify session exists
    verify_session(db, session_id)
    
    # Verify problem exists
    problem = db.query(Problem).filter(Problem.id == attempt.problem_id).first()
    if not problem:
        raise HTTPException(
            status_code=404,
            detail=f"Problem with id {attempt.problem_id} not found"
        )
    
    # Create attempt
    db_attempt = Attempt(
        session_id=session_id,
        problem_id=attempt.problem_id,
        time_seconds=attempt.time_seconds,
        key_strokes=attempt.key_strokes,
        ccpm=attempt.ccpm
    )
    
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    
    return AttemptResponse(
        id=db_attempt.id,
        session_id=db_attempt.session_id,
        problem_id=db_attempt.problem_id,
        time_seconds=db_attempt.time_seconds,
        key_strokes=db_attempt.key_strokes,
        ccpm=db_attempt.ccpm,
        created_at=db_attempt.created_at
    )

