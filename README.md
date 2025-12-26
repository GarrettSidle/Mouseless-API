# Mouseless Backend API

FastAPI backend for the Mouseless application with PostgreSQL database.

## Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   **Troubleshooting installation issues on Windows:**

   - If you encounter errors with `pydantic-core`, try:
     ```bash
     pip install --upgrade pip setuptools wheel
     pip install pydantic --no-build-isolation
     pip install -r requirements.txt
     ```
   - Or install Microsoft C++ Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Alternative: Use a pre-built wheel:
     ```bash
     pip install fastapi uvicorn[standard] sqlalchemy psycopg2-binary pydantic python-dotenv
     ```

2. **Set up PostgreSQL database:**

   - Create a PostgreSQL database named `mouseless`
   - Update the `DATABASE_URL` in `app/database.py` or set it as an environment variable:
     ```bash
     export DATABASE_URL="postgresql://username:password@localhost:5432/mouseless"
     ```

3. **Run database migrations (creates tables):**
   The tables will be automatically created when you start the application, or you can create them manually by running:

   ```python
   from app.database import engine, Base
   Base.metadata.create_all(bind=engine)
   ```

4. **Seed the database with initial problems:**

   ```bash
   python seed_data.py
   ```

   **To reset the database (drop all tables and reseed):**

   ```bash
   python drop_tables.py  # Drops all tables (requires confirmation)
   python seed_data.py    # Reseeds the database
   ```

5. **Start the server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication

- **POST `/api/auth/register`**

  - Creates a new user account
  - Body: `{ "username": "string", "password": "string" }`
  - Password must be at least 6 characters
  - Username must be unique
  - Returns: `{ "id": 1, "username": "...", "created_at": "..." }`
  - No authentication required

- **POST `/api/auth/login`**

  - Authenticate user and create a session
  - Body: `{ "username": "string", "password": "string" }`
  - Returns: `{ "session_id": "...", "created_at": "..." }`
  - No authentication required

- **GET `/api/auth/validate`**
  - Validate a session ID and return the associated username
  - Requires: `X-Session-ID` header
  - Returns: `{ "session_id": "...", "username": "...", "created_at": "..." }`

### Problems

- **GET `/api/problems/random`**
  - Returns a random problem
  - Session ID is optional in `X-Session-ID` header
  - If session ID is provided and valid, includes best attempt stats (`best_time`, `best_key_strokes`, `best_ccpm`)
  - Returns: `{ "id": 1, "name": "...", "original_text": "...", "modified_text": "...", "problem_id": "1", "best_time": 45.5, "best_key_strokes": 120, "best_ccpm": 150.5 }`
  - Best stats are `null` if no session provided or no previous attempts exist

### Attempts

- **POST `/api/attempts`**
  - Stores attempt metrics for a problem
  - Requires: `X-Session-ID` header
  - Body:
    ```json
    {
      "problem_id": 1,
      "time_seconds": 45.5,
      "key_strokes": 120,
      "ccpm": 150.5
    }
    ```
  - Returns: Attempt object with all fields including `id` and `created_at`

## Database Schema

### Problems

- `id` (Integer, Primary Key)
- `name` (String, required)
- `original_text` (Text, required)
- `modified_text` (Text, required)
- `created_at` (DateTime)

### Users

- `id` (Integer, Primary Key)
- `username` (String, unique, required)
- `hashed_password` (String, required) - Password is hashed and salted using bcrypt
- `created_at` (DateTime)

### Sessions

- `session_id` (String, Primary Key, UUID)
- `user_id` (Integer, Foreign Key to Users, required)
- `created_at` (DateTime)
- `last_accessed_at` (DateTime)

### Attempts

- `id` (Integer, Primary Key)
- `session_id` (String, Foreign Key to Sessions)
- `problem_id` (Integer, Foreign Key to Problems)
- `time_seconds` (Float)
- `key_strokes` (Integer)
- `ccpm` (Float - Characters Changed Per Minute)
- `created_at` (DateTime)

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (default: `postgresql://postgres:postgres@localhost:5432/mouseless`)

## Development

The API uses FastAPI's automatic interactive documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
