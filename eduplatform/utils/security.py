import hashlib
import uuid
from datetime import datetime

def hash_password(password: str) -> tuple[str, str]:
    """Hash a password with a randomly generated salt."""
    if not isinstance(password, str) or not password.strip():
        raise ValueError("Password must be a non-empty string")
    
    try:
        salt = uuid.uuid4().hex
        # Ensure consistent encoding
        hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        return hashed, salt
    except Exception as e:
        raise ValueError(f"Failed to hash password: {str(e)}")

def verify_password(hashed_password: str, salt: str, input_password: str) -> bool:
    """Verify a password against its hash and salt."""
    if not all(isinstance(x, str) for x in [hashed_password, salt, input_password]):
        return False
    if not all(x.strip() for x in [hashed_password, salt, input_password]):
        return False
        
    try:
        # Use consistent encoding
        computed_hash = hashlib.sha256((input_password + salt).encode('utf-8')).hexdigest()
        return computed_hash == hashed_password
    except Exception:
        return False

def get_current_iso_date() -> str:
    """Return current date in ISO format."""
    return datetime.now().isoformat()
