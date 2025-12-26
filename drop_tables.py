"""
Script to drop all tables from the database.
Use this to reset the database before reseeding.

WARNING: This will delete all data in the database!
"""
from app.database import engine, Base
from app.models import User, Problem, Session, Attempt

def drop_all_tables():
    """Drop all tables from the database"""
    print("Dropping all tables...")
    
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        print("✓ All tables dropped successfully!")
        print("\nYou can now run 'python seed_data.py' to reseed the database.")
    except Exception as e:
        print(f"✗ Error dropping tables: {e}")
        raise


if __name__ == "__main__":
    import sys
    
    # Confirmation prompt
    print("=" * 60)
    print("WARNING: This will delete ALL data in the database!")
    print("=" * 60)
    
    response = input("Are you sure you want to drop all tables? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        drop_all_tables()
    else:
        print("Operation cancelled.")
        sys.exit(0)

