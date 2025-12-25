"""
Quick start script for the Mouseless backend API.
This script will:
1. Create database tables if they don't exist
2. Seed the database with initial problems (if empty)
3. Start the FastAPI server
"""
import uvicorn
from app.database import engine, Base

if __name__ == "__main__":
    # Create tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")
    
    # Seed database
    print("Seeding database...")
    try:
        from seed_data import seed_problems
        seed_problems()
    except Exception as e:
        print(f"Warning: Could not seed database: {e}")
        print("You can run 'python seed_data.py' manually later.")
    
    # Start server
    print("\nStarting FastAPI server on http://localhost:8000")
    print("API documentation available at http://localhost:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

