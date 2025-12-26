"""
Password hashing utilities using bcrypt
"""
import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with salt.
    Returns the hashed password as a string.
    """
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hashed password.
    Returns True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

