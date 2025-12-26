from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Session as SessionModel
from app.schemas import UserCreate, UserResponse, LoginRequest, LoginResponse, SessionResponse
from app.auth import hash_password, verify_password
from app.dependencies import get_session_id
import uuid
from datetime import datetime, timezone

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.
    Username must be unique. Password will be hashed before storage.
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Validate username and password
    if not user_data.username or len(user_data.username.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username cannot be empty"
        )
    
    if not user_data.password or len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create new user
    db_user = User(
        username=user_data.username.strip(),
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        created_at=db_user.created_at
    )


@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and create a session.
    Returns a session ID that should be stored client-side and included in subsequent requests.
    """
    # Find user by username
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    
    # Create new session linked to user
    db_session = SessionModel(
        session_id=session_id,
        user_id=user.id
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    return LoginResponse(
        session_id=db_session.session_id,
        created_at=db_session.created_at
    )


@router.get("/validate", response_model=SessionResponse)
def validate_session(
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id)
):
    """
    Validate a session ID and return the associated username.
    Requires X-Session-ID header.
    """
    
    # Find session with user relationship loaded
    session = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    # Update last accessed time
    session.last_accessed_at = datetime.now(timezone.utc)
    db.commit()
    
    # Ensure user relationship is loaded
    if not session.user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session user not found"
        )
    
    return SessionResponse(
        session_id=session.session_id,
        username=session.user.username,
        created_at=session.created_at
    )

