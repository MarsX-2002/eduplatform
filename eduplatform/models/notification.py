from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

class NotificationPriority(Enum):
    """Priority levels for notifications."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class NotificationType(Enum):
    """Types of notifications in the system."""
    SYSTEM = "system"
    ASSIGNMENT = "assignment"
    GRADE = "grade"
    ATTENDANCE = "attendance"
    BEHAVIOR = "behavior"
    ANNOUNCEMENT = "announcement"
    REMINDER = "reminder"

class Notification:
    """Class representing a notification in the educational platform."""
    
    def __init__(self, 
                 recipient_id: str,
                 title: str,
                 message: str,
                 notification_type: NotificationType,
                 priority: NotificationPriority = NotificationPriority.NORMAL,
                 related_entity_id: Optional[str] = None,
                 related_entity_type: Optional[str] = None):
        """Initialize a new notification.
        
        Args:
            recipient_id: ID of the user receiving the notification
            title: Notification title
            message: Detailed message
            notification_type: Type of notification
            priority: Priority level
            related_entity_id: Optional ID of related entity (e.g., assignment_id)
            related_entity_type: Type of related entity (e.g., 'assignment', 'grade')
        """
        # Ensure ID is always a string
        self._id = str(id(self))  # Use object's memory address as a unique ID
        self._recipient_id = recipient_id
        self._title = title
        self._message = message
        self._type = notification_type
        self._priority = priority
        self._is_read = False
        self._is_archived = False
        self._created_at = datetime.now()
        self._read_at: Optional[datetime] = None
        self._related_entity_id = related_entity_id
        self._related_entity_type = related_entity_type
        self._metadata: Dict[str, Any] = {}
    
    @property
    def id(self) -> str:
        """Get the notification ID."""
        return self._id
    
    @property
    def recipient_id(self) -> str:
        """Get the recipient's ID."""
        return self._recipient_id
    
    @property
    def is_read(self) -> bool:
        """Check if the notification has been read."""
        return self._is_read
    
    def mark_as_read(self) -> None:
        """Mark the notification as read."""
        if not self._is_read:
            self._is_read = True
            self._read_at = datetime.now()
    
    def mark_as_unread(self) -> None:
        """Mark the notification as unread."""
        self._is_read = False
        self._read_at = None
    
    def archive(self) -> None:
        """Archive the notification."""
        self._is_archived = True
    
    def unarchive(self) -> None:
        """Unarchive the notification."""
        self._is_archived = False
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add or update metadata for the notification."""
        self._metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value by key."""
        return self._metadata.get(key, default)
    
    def to_dict(self, include_metadata: bool = False) -> Dict[str, Any]:
        """Convert the notification to a dictionary.
        
        Args:
            include_metadata: Whether to include metadata in the output
            
        Returns:
            Dictionary representation of the notification
        """
        result = {
            'id': self._id,
            'recipient_id': self._recipient_id,
            'title': self._title,
            'message': self._message,
            'type': self._type.value,
            'priority': self._priority.value,
            'is_read': self._is_read,
            'is_archived': self._is_archived,
            'created_at': self._created_at.isoformat(),
            'related_entity_id': self._related_entity_id,
            'related_entity_type': self._related_entity_type
        }
        
        if self._read_at:
            result['read_at'] = self._read_at.isoformat()
            
        if include_metadata and self._metadata:
            result['metadata'] = self._metadata
            
        return result
    
    @classmethod
    def create_assignment_notification(
        cls,
        recipient_id: str,
        assignment_title: str,
        assignment_id: str,
        action: str = 'created',
        due_date: Optional[datetime] = None
    ) -> 'Notification':
        """Create a notification about an assignment.
        
        Args:
            recipient_id: ID of the recipient
            assignment_title: Title of the assignment
            assignment_id: ID of the assignment
            action: Action performed ('created', 'graded', 'submitted', etc.)
            due_date: Optional due date for the assignment
            
        Returns:
            A new Notification instance
        """
        actions = {
            'created': 'created a new assignment',
            'graded': 'graded your submission for',
            'submitted': 'submitted work for',
            'overdue': 'is overdue for',
            'updated': 'updated the assignment',
            'commented': 'commented on your submission for'
        }
        
        action_text = actions.get(action, 'updated')
        title = f"Assignment {action.capitalize()}"
        message = f"Your teacher has {action_text}: {assignment_title}"
        
        if due_date and action == 'created':
            message += f" (Due: {due_date.strftime('%b %d, %Y %H:%M')})"
            
        notification = cls(
            recipient_id=recipient_id,
            title=title,
            message=message,
            notification_type=NotificationType.ASSIGNMENT,
            priority=NotificationPriority.HIGH if action in ['graded', 'overdue'] else NotificationPriority.NORMAL,
            related_entity_id=assignment_id,
            related_entity_type='assignment'
        )
        
        if action == 'overdue' and due_date:
            notification.add_metadata('days_late', (datetime.now() - due_date).days)
            
        return notification
    
    @classmethod
    def create_grade_notification(
        cls,
        recipient_id: str,
        assignment_title: str,
        grade: float,
        max_grade: float,
        assignment_id: Optional[str] = None
    ) -> 'Notification':
        """Create a notification about a grade."""
        percentage = (grade / max_grade) * 100
        
        return cls(
            recipient_id=recipient_id,
            title="Grade Posted",
            message=f"You received {grade}/{max_grade} ({percentage:.1f}%) for {assignment_title}",
            notification_type=NotificationType.GRADE,
            priority=NotificationPriority.HIGH,
            related_entity_id=assignment_id,
            related_entity_type='grade'
        )
