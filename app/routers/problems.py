from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timezone
from app.database import get_db
from app.models import Problem, Attempt, Session as SessionModel, ProblemHistogram, HistogramDataType
from app.schemas import ProblemResponse
from app.dependencies import get_session_id, verify_session, get_optional_session_id

router = APIRouter()


@router.get("/random", response_model=ProblemResponse)
def get_random_problem(
    db: Session = Depends(get_db),
    session_id: Optional[str] = Depends(get_optional_session_id)
):
    """
    Get a random problem from the database.
    Session ID is optional in the X-Session-ID header.
    If provided and valid, will include best attempt stats for that user.
    Always returns histogram data for the problem (time, strokes, CCPM) if available.
    """
    # Get random problem
    problem = db.query(Problem).order_by(func.random()).first()
    
    if not problem:
        raise HTTPException(
            status_code=404,
            detail="No problems found in database"
        )
    
    # Initialize best stats as None
    best_time = None
    best_key_strokes = None
    best_ccpm = None
    user_id = None
    
    # If session_id is provided, verify it and get user_id
    if session_id:
        session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        if session:
            # Update last accessed time
            session.last_accessed_at = datetime.now(timezone.utc)
            user_id = session.user_id
            db.commit()
            
            # Get best attempt for this problem and user
            # Best time = minimum time_seconds (fastest completion)
            best_attempt = db.query(Attempt).filter(
                Attempt.user_id == user_id,
                Attempt.problem_id == problem.id
            ).order_by(Attempt.time_seconds.asc()).first()
            
            if best_attempt:
                best_time = best_attempt.time_seconds
                best_key_strokes = best_attempt.key_strokes
                best_ccpm = best_attempt.ccpm
    
    # Get histogram data for this problem
    time_histogram = db.query(ProblemHistogram).filter(
        ProblemHistogram.problem_id == problem.id,
        ProblemHistogram.data_type == HistogramDataType.TIME
    ).first()
    
    strokes_histogram = db.query(ProblemHistogram).filter(
        ProblemHistogram.problem_id == problem.id,
        ProblemHistogram.data_type == HistogramDataType.STROKES
    ).first()
    
    ccpm_histogram = db.query(ProblemHistogram).filter(
        ProblemHistogram.problem_id == problem.id,
        ProblemHistogram.data_type == HistogramDataType.CCPM
    ).first()
    
    # Convert to response format (frontend expects problem_id as string)
    return ProblemResponse(
        id=problem.id,
        name=problem.name,
        original_text=problem.original_text,
        modified_text=problem.modified_text,
        problem_id=str(problem.id),  # Frontend expects this as string
        best_time=best_time,
        best_key_strokes=best_key_strokes,
        best_ccpm=best_ccpm,
        time_histogram=list(time_histogram.values) if time_histogram and time_histogram.values else None,
        strokes_histogram=list(strokes_histogram.values) if strokes_histogram and strokes_histogram.values else None,
        ccpm_histogram=list(ccpm_histogram.values) if ccpm_histogram and ccpm_histogram.values else None
    )

