from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# User schemas
class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


# Auth schemas
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    session_id: str
    created_at: datetime


class SessionResponse(BaseModel):
    session_id: str
    username: str
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
    best_time: Optional[float] = None  # Best time in seconds for this user (if logged in)
    best_key_strokes: Optional[int] = None  # Best (minimum) key strokes for this user (if logged in)
    best_ccpm: Optional[float] = None  # Best (maximum) CCPM for this user (if logged in)
    time_histogram: Optional[List[float]] = None  # Histogram data for time (bucketized to 3 seconds)
    strokes_histogram: Optional[List[float]] = None  # Histogram data for strokes (bucketized to 3 keystrokes)
    ccpm_histogram: Optional[List[float]] = None  # Histogram data for CCPM (bucketized to 100 CCPM)

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
    user_id: Optional[int] = None
    problem_id: int
    time_seconds: float
    key_strokes: int
    ccpm: float
    created_at: datetime

    class Config:
        from_attributes = True

