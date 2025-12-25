from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Session as SessionModel
from app.schemas import SessionResponse
import uuid
from datetime import datetime

router = APIRouter()


@router.post("/session", response_model=SessionResponse)
def create_session(db: Session = Depends(get_db)):
    """
    Create a new session and return the session ID.
    The session ID should be stored client-side and included in subsequent requests.
    """
    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    
    # Create new session in database
    db_session = SessionModel(session_id=session_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    return SessionResponse(
        session_id=db_session.session_id,
        created_at=db_session.created_at
    )

