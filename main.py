from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, problems, attempts
import logging

logger = logging.getLogger(__name__)

# Create database tables (with error handling)
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")
    # Don't fail startup, tables might already exist

app = FastAPI(title="Mouseless API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(problems.router, prefix="/api/problems", tags=["problems"])
app.include_router(attempts.router, prefix="/api/attempts", tags=["attempts"])


@app.get("/")
def read_root():
    return {"message": "Mouseless API", "version": "1.0.0"}


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

