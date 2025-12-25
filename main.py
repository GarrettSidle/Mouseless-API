from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, problems, attempts

# Create database tables
Base.metadata.create_all(bind=engine)

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

