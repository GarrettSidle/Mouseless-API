from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone
from app.database import get_db
from app.models import Attempt, Problem, Session as SessionModel, ProblemHistogram, HistogramDataType
from app.schemas import AttemptCreate, AttemptResponse
from app.dependencies import get_optional_session_id

router = APIRouter()


def calculate_bin_index(value: float, bin_width: float) -> int:
    """
    Calculate which bin index a value belongs to based on bin width.
    First bar (bin 0) covers 0 to bin_width/2.
    Subsequent bars cover bin_width intervals.
    For example, with bin_width=2.5:
    - value 0-1.25 -> bin 0 (first bar, half interval)
    - value 1.25-3.75 -> bin 1 (round((2.5-1.25)/2.5) + 1 = 1)
    - value 3.75-6.25 -> bin 2 (round((5-1.25)/2.5) + 1 = 2)
    """
    half_width = bin_width / 2.0
    if value <= half_width:
        return 0
    # For values > half_width, calculate bin index
    return int(round((value - half_width) / bin_width)) + 1


def update_histogram(db: Session, problem_id: int, data_type: HistogramDataType, new_value: float):
    """
    Update or create histogram data for a problem.
    Stores histogram as an array where each index represents a bin, and the value is the count.
    Only stores the first 25 bars (indices 0-24). Data beyond that is ignored.
    - Time: bin width = 2.5 seconds (bin 0 = 0-1.25s, bin 1 = 1.25-3.75s, bin 2 = 3.75-6.25s, etc.)
    - Strokes: bin width = 5 keystrokes (bin 0 = 0-2.5, bin 1 = 2.5-7.5, bin 2 = 7.5-12.5, etc.)
    - CCPM: bin width = 100 (bin 0 = 0-50, bin 1 = 50-150, bin 2 = 150-250, etc.)
    """
    MAX_BARS = 25  # Maximum number of bars to store (indices 0-24)
    
    # Determine bin width based on data type
    bin_widths = {
        HistogramDataType.TIME: 2.5,      # 2.5 seconds
        HistogramDataType.STROKES: 5.0,   # 5 keystrokes
        HistogramDataType.CCPM: 100.0     # 100 CCPM
    }
    
    bin_width = bin_widths.get(data_type, 1.0)
    bin_index = calculate_bin_index(new_value, bin_width)
    
    # Ignore data that would be stored beyond the 25th bar (index >= 25)
    if bin_index >= MAX_BARS:
        return  # Ignore this value
    
    histogram = db.query(ProblemHistogram).filter(
        ProblemHistogram.problem_id == problem_id,
        ProblemHistogram.data_type == data_type
    ).first()
    
    if histogram:
        # Get existing counts array or initialize empty array
        if histogram.values is None:
            counts = []
        else:
            counts = list(histogram.values)
        
        # Extend array if needed to accommodate this bin index (but cap at MAX_BARS)
        while len(counts) <= bin_index and len(counts) < MAX_BARS:
            counts.append(0)
        
        # Increment count for this bin (we already checked bin_index < MAX_BARS)
        if bin_index < len(counts):
            counts[bin_index] = counts[bin_index] + 1
        
        # Ensure array doesn't exceed MAX_BARS (trim if somehow it does)
        if len(counts) > MAX_BARS:
            counts = counts[:MAX_BARS]
        
        histogram.values = counts
    else:
        # Create new histogram entry with initial count for this bin
        counts = [0] * (bin_index + 1)  # Initialize array with zeros up to bin_index
        counts[bin_index] = 1  # Set count for this bin to 1
        histogram = ProblemHistogram(
            problem_id=problem_id,
            data_type=data_type,
            values=counts
        )
        db.add(histogram)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_attempt(
    attempt: AttemptCreate,
    db: Session = Depends(get_db),
    session_id: Optional[str] = Depends(get_optional_session_id)
):
    """
    Store attempt metrics for a problem.
    Session ID is optional in the X-Session-ID header.
    If provided, it will be validated and the user_id will be extracted and stored.
    The attempt data will be added to the problem's histogram statistics.
    """
    # Get user_id from session if provided
    user_id = None
    if session_id:
        session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        if session:
            # Update last accessed time
            session.last_accessed_at = datetime.now(timezone.utc)
            user_id = session.user_id
            db.commit()
        # If session doesn't exist, continue without user_id (allow unauthenticated attempts)
    
    # Verify problem exists
    problem = db.query(Problem).filter(Problem.id == attempt.problem_id).first()
    if not problem:
        raise HTTPException(
            status_code=404,
            detail=f"Problem with id {attempt.problem_id} not found"
        )
    
    # Only create attempt if user is logged in (user_id is not None)
    db_attempt = None
    if user_id is not None:
        db_attempt = Attempt(
            user_id=user_id,
            problem_id=attempt.problem_id,
            time_seconds=attempt.time_seconds,
            key_strokes=attempt.key_strokes,
            ccpm=attempt.ccpm
        )
        db.add(db_attempt)
    
    # Always update histogram data for this problem (even if user is not logged in)
    update_histogram(db, attempt.problem_id, HistogramDataType.TIME, attempt.time_seconds)
    update_histogram(db, attempt.problem_id, HistogramDataType.STROKES, float(attempt.key_strokes))
    update_histogram(db, attempt.problem_id, HistogramDataType.CCPM, attempt.ccpm)
    
    # Commit all changes (attempt + histogram updates) together
    db.commit()
    
    # If attempt was created, refresh it and return response
    if db_attempt:
        db.refresh(db_attempt)
        return AttemptResponse(
            id=db_attempt.id,
            user_id=db_attempt.user_id,
            problem_id=db_attempt.problem_id,
            time_seconds=db_attempt.time_seconds,
            key_strokes=db_attempt.key_strokes,
            ccpm=db_attempt.ccpm,
            created_at=db_attempt.created_at
        )
    else:
        # User not logged in - histogram updated but no attempt record created
        # Return 204 No Content to indicate success but no body
        from fastapi import Response
        return Response(status_code=status.HTTP_204_NO_CONTENT)

