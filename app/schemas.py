from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Session schemas
class SessionCreate(BaseModel):
    pass  # Session ID will be generated server-side


class SessionResponse(BaseModel):
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Problem schemas
class ProblemResponse(BaseModel):
    id: int
    name: str
    original_text: str
    modified_text: str
    problem_id: str  # For frontend compatibility, this will be the string representation of id
    best_time: Optional[float] = None  # Best time in seconds for this session (if session provided)
    best_key_strokes: Optional[int] = None  # Best (minimum) key strokes for this session (if session provided)
    best_ccpm: Optional[float] = None  # Best (maximum) CCPM for this session (if session provided)

    class Config:
        from_attributes = True


# Attempt schemas
class AttemptCreate(BaseModel):
    problem_id: int
    time_seconds: float
    key_strokes: int
    ccpm: float


class AttemptResponse(BaseModel):
    id: int
    session_id: str
    problem_id: int
    time_seconds: float
    key_strokes: int
    ccpm: float
    created_at: datetime

    class Config:
        from_attributes = True

