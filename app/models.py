from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sessions = relationship("Session", back_populates="user")
    attempts = relationship("Attempt", back_populates="user")


class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    original_text = Column(Text, nullable=False)
    modified_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    attempts = relationship("Attempt", back_populates="problem")
    histograms = relationship("ProblemHistogram", back_populates="problem", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(String(255), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="sessions")


class HistogramDataType(enum.Enum):
    TIME = "time"
    STROKES = "strokes"
    CCPM = "ccpm"


class ProblemHistogram(Base):
    __tablename__ = "problem_histograms"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    data_type = Column(SQLEnum(HistogramDataType), nullable=False, index=True)
    values = Column(ARRAY(Float), nullable=False, default=[])  # Array of float values
    
    # Relationships
    problem = relationship("Problem", back_populates="histograms")
    
    __table_args__ = (
        UniqueConstraint('problem_id', 'data_type', name='uq_problem_histogram'),
    )


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    time_seconds = Column(Float, nullable=False)
    key_strokes = Column(Integer, nullable=False)
    ccpm = Column(Float, nullable=False)  # Characters Changed Per Minute
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="attempts")
    problem = relationship("Problem", back_populates="attempts")

