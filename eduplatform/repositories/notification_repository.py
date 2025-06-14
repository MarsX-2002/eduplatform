from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from ..models.notification import Notification, NotificationPriority, NotificationType
from .base import BaseRepository

class NotificationRepository(BaseRepository[Notification]):
    """Repository for managing Notification entities."""
    
    def _get_key(self, item: Notification) -> str:
        """Get the unique key for a notification (its ID)."""
        return item._id
    
    def get_user_notifications(self, 
                             user_id: str, 
                             unread_only: bool = False,
                             limit: Optional[int] = None) -> List[Notification]:
        """Get notifications for a specific user.
        
        Args:
            user_id: ID of the user
            unread_only: Whether to return only unread notifications
            limit: Maximum number of notifications to return
            
        Returns:
            List of notifications, optionally filtered and limited
        """
        notifications = [
            n for n in self.get_all() 
            if n._recipient_id == user_id and 
               (not unread_only or not n._is_read)
        ]
        
        # Sort by creation date (newest first)
        notifications.sort(key=lambda x: x._created_at, reverse=True)
        
        return notifications[:limit] if limit is not None else notifications
    
    def mark_as_read(self, notification_id: str) -> bool:
        """Mark a notification as read.
        
        Args:
            notification_id: ID of the notification to mark as read
            
        Returns:
            bool: True if notification was found and updated, False otherwise
        """
        notification = self.get(notification_id)
        if notification:
            notification.mark_as_read()
            return True
        return False
    
    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications for a user as read.
        
        Args:
            user_id: ID of the user
            
        Returns:
            int: Number of notifications marked as read
        """
        count = 0
        for notification in self.get_all():
            if notification._recipient_id == user_id and not notification._is_read:
                notification.mark_as_read()
                count += 1
        return count
    
    def get_unread_count(self, user_id: str) -> int:
        """Get the count of unread notifications for a user."""
        return len([
            n for n in self.get_all() 
            if n._recipient_id == user_id and not n._is_read
        ])
    
    def get_recent_notifications(self, 
                               user_id: str, 
                               days: int = 7,
                               limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent notifications for a user within a time period.
        
        Args:
            user_id: ID of the user
            days: Number of days to look back
            limit: Maximum number of notifications to return
            
        Returns:
            List of notification dictionaries with basic information
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        notifications = [
            n for n in self.get_all()
            if n._recipient_id == user_id and n._created_at >= cutoff_date
        ]
        
        # Sort by creation date (newest first)
        notifications.sort(key=lambda x: x._created_at, reverse=True)
        
        # Convert to simplified dictionary format
        return [
            {
                'id': n._id,
                'title': n._title,
                'message': n._message,
                'type': n._type.value,
                'priority': n._priority.value,
                'is_read': n._is_read,
                'created_at': n._created_at.isoformat(),
                'related_entity_id': n._related_entity_id,
                'related_entity_type': n._related_entity_type
            }
            for n in notifications[:limit]
        ]
    
    def create_notification(self, 
                          recipient_id: str,
                          title: str,
                          message: str,
                          notification_type: Union[NotificationType, str],
                          priority: Union[NotificationPriority, str] = NotificationPriority.NORMAL,
                          related_entity_id: Optional[str] = None,
                          related_entity_type: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> Notification:
        """Create and store a new notification.
        
        Args:
            recipient_id: ID of the recipient user
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            priority: Priority level
            related_entity_id: Optional ID of related entity
            related_entity_type: Type of related entity
            metadata: Additional metadata
            
        Returns:
            The created Notification instance
        """
        if isinstance(notification_type, str):
            notification_type = NotificationType(notification_type.lower())
            
        if isinstance(priority, str):
            priority = NotificationPriority(priority.lower())
        
        notification = Notification(
            recipient_id=recipient_id,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            related_entity_id=related_entity_id,
            related_entity_type=related_entity_type
        )
        
        if metadata:
            for key, value in metadata.items():
                notification.add_metadata(key, value)
                
        self.add(notification)
        return notification
    
    def get_notifications_by_type(self, 
                                user_id: str,
                                notification_type: Union[NotificationType, str],
                                limit: Optional[int] = None) -> List[Notification]:
        """Get notifications of a specific type for a user."""
        if isinstance(notification_type, str):
            notification_type = NotificationType(notification_type.lower())
            
        notifications = [
            n for n in self.get_all()
            if n._recipient_id == user_id and n._type == notification_type
        ]
        
        notifications.sort(key=lambda x: x._created_at, reverse=True)
        return notifications[:limit] if limit is not None else notifications
    
    def cleanup_old_notifications(self, days: int = 90) -> int:
        """Remove notifications older than the specified number of days.
        
        Args:
            days: Number of days to keep notifications
            
        Returns:
            int: Number of notifications removed
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        to_remove = [n._id for n in self.get_all() if n._created_at < cutoff_date]
        
        for notification_id in to_remove:
            self.delete(notification_id)
            
        return len(to_remove)
