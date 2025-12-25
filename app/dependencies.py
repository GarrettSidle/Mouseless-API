from fastapi import Header, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Session as SessionModel
from datetime import datetime, timezone
from typing import Optional


def get_session_id(x_session_id: Optional[str] = Header(None)) -> str:
    """
    Dependency to extract and validate session ID from header.
    If no session ID is provided, raises 401.
    Expects header: X-Session-ID (FastAPI automatically converts x_session_id to X-Session-ID)
    """
    if not x_session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session ID required. Please include X-Session-ID header."
        )
    return x_session_id


def verify_session(db: Session, session_id: str) -> SessionModel:
    """
    Verify that the session exists and update last_accessed_at.
    Raises 401 if session doesn't exist.
    """
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    # Update last accessed time
    session.last_accessed_at = datetime.now(timezone.utc)
    db.commit()
    
    return session

