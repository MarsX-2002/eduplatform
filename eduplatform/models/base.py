from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime
from uuid import uuid4

class AbstractRole(ABC):
    """Abstract base class for all user roles in the system."""
    
    def __init__(self, full_name: str, email: str, password: str):
        """Initialize a new user with basic information."""
        self._id = str(uuid4().int)[:8]  # Generate a shorter ID
        self._full_name = full_name
        self._email = email
        
        # Ensure password is a string and not empty
        if not isinstance(password, str) or not password.strip():
            raise ValueError("Password must be a non-empty string")
            
        try:
            self._password_hash, self._salt = self._hash_password(password)
        except Exception as e:
            raise ValueError(f"Error hashing password: {str(e)}")
            
        self._created_at = datetime.now().isoformat()
        self._notifications = []
    
    @staticmethod
    def _hash_password(password: str) -> tuple[str, str]:
        """Hash the password with a salt."""
        from ..utils.security import hash_password
        return hash_password(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify if the provided password matches the stored hash."""
        from ..utils.security import verify_password
        return verify_password(self._password_hash, self._salt, password)
    
    @abstractmethod
    def get_profile(self) -> Dict[str, Any]:
        """Return the user's profile information."""
        return {
            'id': self._id,
            'full_name': self._full_name,
            'email': self._email,
            'created_at': self._created_at,
            'role': self.__class__.__name__
        }
    
    def update_profile(self, **kwargs) -> None:
        """Update user profile information."""
        allowed_updates = ['_full_name', '_email']
        for key, value in kwargs.items():
            attr = f'_{key}'
            if attr in allowed_updates and hasattr(self, attr):
                setattr(self, attr, value)
    
    def add_notification(self, message: str) -> None:
        """Add a new notification for the user."""
        notification = {
            'id': str(uuid4().int)[:6],
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'read': False
        }
        self._notifications.append(notification)
    
    def view_notifications(self, unread_only: bool = False) -> list:
        """View user's notifications."""
        if unread_only:
            return [n for n in self._notifications if not n['read']]
        return self._notifications
    
    def mark_notification_read(self, notification_id: str) -> bool:
        """Mark a notification as read."""
        for notification in self._notifications:
            if notification['id'] == notification_id:
                notification['read'] = True
                return True
        return False
    
    def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification."""
        for i, notification in enumerate(self._notifications):
            if notification['id'] == notification_id:
                self._notifications.pop(i)
                return True
        return False
