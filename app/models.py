from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to sessions
    sessions = relationship("Session", back_populates="user")


class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    original_text = Column(Text, nullable=False)
    modified_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to attempts
    attempts = relationship("Attempt", back_populates="problem")


class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(String(255), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="sessions")
    attempts = relationship("Attempt", back_populates="session")


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), ForeignKey("sessions.session_id"), nullable=False, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    time_seconds = Column(Float, nullable=False)
    key_strokes = Column(Integer, nullable=False)
    ccpm = Column(Float, nullable=False)  # Characters Changed Per Minute
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("Session", back_populates="attempts")
    problem = relationship("Problem", back_populates="attempts")

