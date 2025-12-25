from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Problem
from app.schemas import ProblemResponse
from app.dependencies import get_session_id, verify_session

router = APIRouter()


@router.get("/random", response_model=ProblemResponse)
def get_random_problem(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id)
):
    """
    Get a random problem from the database.
    Requires a valid session ID in the X-Session-ID header.
    """
    # Verify session exists
    verify_session(db, session_id)
    
    # Get random problem
    problem = db.query(Problem).order_by(func.random()).first()
    
    if not problem:
        raise HTTPException(
            status_code=404,
            detail="No problems found in database"
        )
    
    # Convert to response format (frontend expects problem_id as string)
    return ProblemResponse(
        id=problem.id,
        name=problem.name,
        original_text=problem.original_text,
        modified_text=problem.modified_text,
        problem_id=str(problem.id)  # Frontend expects this as string
    )

