from typing import Dict, Any, List, Optional
from .base import AbstractRole
from enum import Enum, auto

class UserRole(Enum):
    """Enumeration of possible user roles in the system."""
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"

class User(AbstractRole):
    """Base user class that extends AbstractRole with common user functionality."""
    
    def __init__(self, full_name: str, email: str, password: str, role: UserRole):
        """Initialize a new user with a specific role."""
        super().__init__(full_name, email, password)
        self._role = role
        self._phone: Optional[str] = None
        self._address: Optional[str] = None
    
    @property
    def role(self) -> UserRole:
        """Get the user's role."""
        return self._role
    
    def get_profile(self) -> Dict[str, Any]:
        """Return the user's profile information including role-specific data."""
        base_profile = super().get_profile()
        base_profile.update({
            'role': self._role.value,
            'phone': self._phone,
            'address': self._address
        })
        return base_profile
    
    def update_profile(self, **kwargs) -> None:
        """Update user profile information with additional fields."""
        super().update_profile(**kwargs)
        allowed_updates = ['phone', 'address']
        for key, value in kwargs.items():
            if key in allowed_updates and hasattr(self, f'_{key}'):
                setattr(self, f'_{key}', value)
    
    def __str__(self) -> str:
        """String representation of the user."""
        return f"{self._full_name} ({self._email}) - {self._role.value.capitalize()}"
