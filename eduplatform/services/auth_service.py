from typing import Optional, Dict, Any, Type, Union
from datetime import datetime, timedelta
import jwt
from ..models.user import User, UserRole
from ..models.student import Student
from ..models.teacher import Teacher
from ..models.parent import Parent
from ..models.admin import Admin
from ..repositories.user_repository import UserRepository
from ..repositories.notification_repository import NotificationRepository

class AuthService:
    """Service for handling authentication and user management."""
    
    def __init__(self, 
                 user_repository: UserRepository,
                 notification_repository: NotificationRepository,
                 jwt_secret: str,
                 jwt_expire_hours: int = 24):
        """Initialize the auth service with required repositories and configuration."""
        self.user_repo = user_repository
        self.notification_repo = notification_repository
        self.jwt_secret = jwt_secret
        self.jwt_expire_hours = jwt_expire_hours
    
    def register_user(self, 
                     user_type: Type[Union[Student, Teacher, Parent, Admin]],
                     full_name: str,
                     email: str,
                     password: str,
                     **kwargs) -> Dict[str, Any]:
        """Register a new user.
        
        Args:
            user_type: Type of user to create (Student, Teacher, Parent, or Admin)
            full_name: User's full name
            email: User's email (must be unique)
            password: User's password (will be hashed)
            **kwargs: Additional fields specific to the user type
            
        Returns:
            Dictionary containing the created user and auth token
            
        Raises:
            ValueError: If email is already registered or validation fails
        """
        print(f"[AUTH] register_user called with: {user_type}, {full_name}, {email}, {kwargs}")
        
        # Check if email is already registered
        print(f"[AUTH] Checking if email exists: {email}")
        if self.user_repo.email_exists(email):
            print(f"[AUTH] Email {email} already exists")
            raise ValueError("Email already registered")
            
        print(f"[AUTH] Email {email} is available")
        
        # Create the appropriate user type
        print(f"[AUTH] Creating user of type: {user_type.__name__}")
        try:
            if user_type == Student:
                if 'grade' not in kwargs:
                    raise ValueError("Grade is required for student registration")
                user = Student(full_name, email, password, kwargs['grade'])
                print(f"[AUTH] Created Student: {user}")
            elif user_type == Teacher:
                user = Teacher(full_name, email, password)
                print(f"[AUTH] Created Teacher: {user}")
            elif user_type == Parent:
                user = Parent(full_name, email, password)
                print(f"[AUTH] Created Parent: {user}")
            elif user_type == Admin:
                user = Admin(full_name, email, password)
                print(f"[AUTH] Created Admin: {user}")
            else:
                raise ValueError(f"Invalid user type: {user_type.__name__}")
        except Exception as e:
            print(f"[AUTH] Error creating user: {str(e)}")
            print(f"[AUTH] Exception type: {type(e).__name__}")
            raise
        
        # Add any additional profile information
        print("[AUTH] Adding additional profile information")
        if 'phone' in kwargs:
            user._phone = kwargs['phone']
            print(f"[AUTH] Set phone: {kwargs['phone']}")
        if 'address' in kwargs:
            user._address = kwargs['address']
            print(f"[AUTH] Set address: {kwargs['address']}")
        
        # Save the user
        print("[AUTH] Adding user to repository")
        try:
            self.user_repo.add(user)
            print("[AUTH] User added to repository successfully")
        except Exception as e:
            print(f"[AUTH] Error adding user to repository: {str(e)}")
            print(f"[AUTH] Exception type: {type(e).__name__}")
            raise
        
        # Send welcome notification
        print("[AUTH] Sending welcome notification")
        welcome_message = f"Welcome to EduPlatform, {full_name}! Your account has been successfully created."
        try:
            # Use the user's ID as the recipient ID instead of email
            notification = self.notification_repo.create_notification(
                recipient_id=user._id,  # Use the user's ID instead of email
                title="Welcome to EduPlatform",
                message=welcome_message,
                notification_type="system"
            )
            print(f"[AUTH] Created notification: {notification}")
        except Exception as e:
            print(f"[AUTH] Error creating notification: {str(e)}")
            print(f"[AUTH] Exception type: {type(e).__name__}")
            # Don't fail registration if notification fails
        
        # Generate auth token
        token = self._generate_token(user)
        
        return {
            'user': user,
            'token': token,
            'user_type': self.user_repo.get_user_type(user)
        }
    
    def login(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user and return user data with auth token.
        
        Args:
            email: User's email
            password: User's password
            
        Returns:
            Dictionary with user data and token if authentication succeeds, None otherwise
        """
        user = self.user_repo.authenticate(email, password)
        if not user:
            return None
            
        # Generate auth token
        token = self._generate_token(user)
        
        return {
            'user': user,
            'token': token,
            'user_type': self.user_repo.get_user_type(user)
        }
    
    def reset_password_request(self, email: str) -> bool:
        """Initiate a password reset request.
        
        Args:
            email: User's email address
            
        Returns:
            bool: True if request was processed (regardless of whether email exists)
        """
        user = self.user_repo.get_by_email(email)
        if user:
            # In a real implementation, we would generate a reset token and send an email
            # For this example, we'll just create a notification
            reset_token = f"reset_{len(str(hash(str(datetime.now()))))[-10:]}"
            reset_url = f"https://eduplatform.example.com/reset-password?token={reset_token}"
            
            self.notification_repo.create_notification(
                recipient_id=email,
                title="Password Reset Request",
                message=f"Click the following link to reset your password: {reset_url}",
                notification_type="system",
                metadata={
                    'reset_token': reset_token,
                    'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()
                }
            )
            
        # Always return True to avoid revealing whether the email exists
        return True
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset a user's password using a valid reset token.
        
        Args:
            token: Password reset token
            new_password: New password
            
        Returns:
            bool: True if password was reset successfully, False if token is invalid
        """
        # In a real implementation, we would validate the token and its expiration
        # For this example, we'll just check if it starts with 'reset_'
        if not token.startswith('reset_'):
            return False
            
        # Extract user ID from token (in a real app, this would be more secure)
        user_email = token.split('_')[-1]
        user = self.user_repo.get_by_email(user_email)
        
        if not user:
            return False
            
        # Update password
        user._password_hash, user._salt = user._hash_password(new_password)
        self.user_repo.update(user)
        
        # Notify user of password change
        self.notification_repo.create_notification(
            recipient_id=user_email,
            title="Password Changed",
            message="Your password has been successfully changed. If you didn't make this change, please contact support immediately.",
            notification_type="security"
        )
        
        return True
    
    def _generate_token(self, user: User) -> str:
        """Generate a JWT token for the user."""
        payload = {
            'user_id': user._email,  # Using email as user ID
            'role': user._role.value if hasattr(user, '_role') else 'user',
            'exp': datetime.utcnow() + timedelta(hours=self.jwt_expire_hours)
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify a JWT token and return the decoded payload if valid."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_current_user(self, token: str) -> Optional[User]:
        """Get the current user from a JWT token."""
        payload = self.verify_token(token)
        if not payload:
            return None
            
        return self.user_repo.get_by_email(payload['user_id'])
    
    def update_profile(self, 
                     user: User, 
                     full_name: Optional[str] = None,
                     email: Optional[str] = None,
                     phone: Optional[str] = None,
                     address: Optional[str] = None) -> User:
        """Update a user's profile information.
        
        Args:
            user: The user to update
            full_name: New full name (if provided)
            email: New email (if provided)
            phone: New phone number (if provided)
            address: New address (if provided)
            
        Returns:
            The updated user object
            
        Raises:
            ValueError: If email is already taken by another user
        """
        if email and email != user._email and self.user_repo.email_exists(email):
            raise ValueError("Email already in use by another account")
            
        if full_name:
            user._full_name = full_name
        if email:
            user._email = email
        if phone is not None:
            user._phone = phone
        if address is not None:
            user._address = address
            
        self.user_repo.update(user)
        
        # Log the profile update
        self.notification_repo.create_notification(
            recipient_id=user._email,
            title="Profile Updated",
            message="Your profile information has been updated successfully.",
            notification_type="account"
        )
        
        return user
