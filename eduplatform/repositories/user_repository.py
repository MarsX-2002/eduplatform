from typing import Dict, List, Optional, Type, TypeVar, Union
from ..models.user import User, UserRole
from ..models.student import Student
from ..models.teacher import Teacher
from ..models.parent import Parent
from ..models.admin import Admin
from .base import BaseRepository

T = TypeVar('T', bound=User)

class UserRepository(BaseRepository[User]):
    """Repository for managing User entities and their derived classes."""
    
    def _get_key(self, item: User) -> str:
        """Get the unique key for a user (email)."""
        if hasattr(item, '_email') and item._email is not None:
            return str(item._email)
        # If no email is set (shouldn't happen for valid users), use a temporary key
        return f"temp_{id(item)}"
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by their email address."""
        return self.get(email)
    
    def get_by_role(self, role: Union[UserRole, str]) -> List[User]:
        """Get all users with a specific role."""
        if isinstance(role, str):
            role = UserRole(role.lower())
        return [user for user in self.get_all() if hasattr(user, '_role') and user._role == role]
    
    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
        user = self.get(email)
        if user and hasattr(user, 'verify_password') and user.verify_password(password):
            return user
        return None
    
    def email_exists(self, email: str) -> bool:
        """Check if a user with the given email already exists."""
        return self.exists(email)
    
    def get_students(self) -> List[Student]:
        """Get all student users."""
        return [user for user in self.get_all() if isinstance(user, Student)]
    
    def get_teachers(self) -> List[Teacher]:
        """Get all teacher users."""
        return [user for user in self.get_all() if isinstance(user, Teacher)]
    
    def get_parents(self) -> List[Parent]:
        """Get all parent users."""
        return [user for user in self.get_all() if isinstance(user, Parent)]
    
    def get_admins(self) -> List[Admin]:
        """Get all admin users."""
        return [user for user in self.get_all() if isinstance(user, Admin)]
    
    def search_users(self, query: str, role: Optional[UserRole] = None) -> List[User]:
        """Search users by name or email, optionally filtered by role."""
        query = query.lower()
        results = []
        
        for user in self.get_all():
            # Skip if role filter is provided and doesn't match
            if role is not None and (not hasattr(user, '_role') or user._role != role):
                continue
                
            # Check if query matches name or email
            if (query in user._full_name.lower()) or (query in user._email.lower()):
                results.append(user)
                
        return results
    
    def get_user_type(self, user: User) -> str:
        """Get the type of user as a string."""
        if isinstance(user, Student):
            return 'student'
        elif isinstance(user, Teacher):
            return 'teacher'
        elif isinstance(user, Parent):
            return 'parent'
        elif isinstance(user, Admin):
            return 'admin'
        return 'unknown'
