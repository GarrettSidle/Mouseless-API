"""
Seed script to populate the database with problems from the frontend temp data.
Run this after creating the database tables.
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Problem

# Sample problems from the frontend Editor.tsx
PROBLEMS_DATA = [
    {
        "name": "Remove Interface Property",
        "original_text": "interface TimerState {\n   time: number;\n   isRunning: boolean;\n}",
        "modified_text": "interface TimerState {\n   time: number;\n}",
    },
    {
        "name": "Add Character",
        "original_text": "1",
        "modified_text": "12",
    },
    {
        "name": "Change Number",
        "original_text": "1",
        "modified_text": "2",
    },
    {
        "name": "Extend Number",
        "original_text": "3",
        "modified_text": "355",
    },
    {
        "name": "Refactor Variable Names",
        "original_text": "function calculateTotal(items) {\n  let sum = 0;\n  for (let i = 0; i < items.length; i++) {\n    sum += items[i].price;\n  }\n  return sum;\n}\n\nfunction applyDiscount(total) {\n  return total * 0.9;\n}",
        "modified_text": "function calculateTotal(items) {\n  let total = 0;\n  for (let i = 0; i < items.length; i++) {\n    total += items[i].price;\n  }\n  return total;\n}\n\nfunction applyDiscount(amount) {\n  return amount * 0.9;\n}",
    },
    {
        "name": "Reorder Methods",
        "original_text": "class UserService {\n  constructor() {\n    this.users = [];\n    this.nextId = 1;\n  }\n\n  addUser(name, email) {\n    const user = {\n      id: this.nextId++,\n      name: name,\n      email: email\n    };\n    this.users.push(user);\n    return user;\n  }\n\n  findUserById(id) {\n    return this.users.find(u => u.id === id);\n  }\n\n  getAllUsers() {\n    return this.users;\n  }\n}",
        "modified_text": "class UserService {\n  constructor() {\n    this.users = [];\n    this.nextId = 1;\n  }\n\n  getAllUsers() {\n    return this.users;\n  }\n\n  findUserById(id) {\n    return this.users.find(u => u.id === id);\n  }\n\n  addUser(name, email) {\n    const user = {\n      id: this.nextId++,\n      name: name,\n      email: email\n    };\n    this.users.push(user);\n    return user;\n  }\n}",
    },
    {
        "name": "Refactor Parameter Names",
        "original_text": "const data = [\n  { id: 1, name: 'Alice', age: 25 },\n  { id: 2, name: 'Bob', age: 30 },\n  { id: 3, name: 'Charlie', age: 35 }\n];\n\nfunction processData(data) {\n  const results = [];\n  for (let item of data) {\n    if (item.age > 28) {\n      results.push(item.name);\n    }\n  }\n  return results;\n}\n\nconsole.log(processData(data));",
        "modified_text": "const data = [\n  { id: 1, name: 'Alice', age: 25 },\n  { id: 2, name: 'Bob', age: 30 },\n  { id: 3, name: 'Charlie', age: 35 }\n];\n\nfunction processData(users) {\n  const filtered = [];\n  for (let user of users) {\n    if (user.age > 28) {\n      filtered.push(user.name);\n    }\n  }\n  return filtered;\n}\n\nconsole.log(processData(data));",
    },
    {
        "name": "Add Error Handling",
        "original_text": "async function fetchUserData(userId) {\n  try {\n    const response = await fetch(`/api/users/${userId}`);\n    const data = await response.json();\n    return data;\n  } catch (error) {\n    console.error('Error:', error);\n    return null;\n  }\n}\n\nasync function fetchUserPosts(userId) {\n  try {\n    const response = await fetch(`/api/users/${userId}/posts`);\n    const data = await response.json();\n    return data;\n  } catch (error) {\n    console.error('Error:', error);\n    return null;\n  }\n}",
        "modified_text": "async function fetchUserData(userId) {\n  try {\n    const response = await fetch(`/api/users/${userId}`);\n    if (!response.ok) {\n      throw new Error(`HTTP error! status: ${response.status}`);\n    }\n    const data = await response.json();\n    return data;\n  } catch (error) {\n    console.error('Error:', error);\n    return null;\n  }\n}\n\nasync function fetchUserPosts(userId) {\n  try {\n    const response = await fetch(`/api/users/${userId}/posts`);\n    const data = await response.json();\n    return data;\n  } catch (error) {\n    console.error('Error:', error);\n    return null;\n  }\n}",
    },
    {
        "name": "Rename Regex Variable",
        "original_text": "function validateEmail(email) {\n  if (!email) return false;\n  const regex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;\n  return regex.test(email);\n}\n\nfunction validatePassword(password) {\n  if (!password) return false;\n  if (password.length < 8) return false;\n  return true;\n}\n\nfunction validateUser(user) {\n  return validateEmail(user.email) && validatePassword(user.password);\n}",
        "modified_text": "function validateEmail(email) {\n  if (!email) return false;\n  const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;\n  return emailRegex.test(email);\n}\n\nfunction validatePassword(password) {\n  if (!password) return false;\n  if (password.length < 8) return false;\n  return true;\n}\n\nfunction validateUser(user) {\n  return validateEmail(user.email) && validatePassword(user.password);\n}",
    },
]


def seed_problems():
    """Seed the database with problems"""
    db: Session = SessionLocal()
    
    try:
        # Check if problems already exist
        existing_count = db.query(Problem).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} problems. Skipping seed.")
            return
        
        # Add all problems
        for problem_data in PROBLEMS_DATA:
            problem = Problem(
                name=problem_data["name"],
                original_text=problem_data["original_text"],
                modified_text=problem_data["modified_text"]
            )
            db.add(problem)
        
        db.commit()
        print(f"Successfully seeded {len(PROBLEMS_DATA)} problems into the database.")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Ensure tables are created
    Base.metadata.create_all(bind=engine)
    seed_problems()

