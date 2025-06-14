from typing import Dict, List, Optional, Any
from .user import User, UserRole
from datetime import datetime

class Parent(User):
    """Parent class representing a parent in the educational platform."""
    
    def __init__(self, full_name: str, email: str, password: str):
        """Initialize a new parent.
        
        Args:
            full_name: Parent's full name
            email: Parent's email (must be unique)
            password: Parent's password (will be hashed)
        """
        super().__init__(full_name, email, password, UserRole.PARENT)
        self._children: List[Dict[str, Any]] = []  # List of child student IDs and their basic info
        self._notification_preferences: Dict[str, bool] = {
            'assignment_due': True,
            'grade_posted': True,
            'attendance_issue': True,
            'behavior_note': True
        }
    
    def add_child(self, student_id: str, student_name: str, relationship: str) -> bool:
        """Add a child to the parent's account.
        
        Args:
            student_id: ID of the student (child)
            student_name: Full name of the student
            relationship: Relationship to the student (e.g., 'mother', 'father', 'guardian')
            
        Returns:
            bool: True if added, False if child already exists
        """
        if any(child['id'] == student_id for child in self._children):
            return False
            
        self._children.append({
            'id': student_id,
            'name': student_name,
            'relationship': relationship,
            'last_checked': datetime.now().isoformat()
        })
        return True
    
    def get_children(self) -> List[Dict[str, Any]]:
        """Get list of all children with basic info."""
        return [{
            'id': child['id'],
            'name': child['name'],
            'relationship': child['relationship']
        } for child in self._children]
    
    def view_child_grades(self, child_id: str, subject: Optional[str] = None) -> Dict[str, Any]:
        """View a child's grades.
        
        Args:
            child_id: ID of the child
            subject: Optional subject to filter by
            
        Returns:
            Dict with child's grade information
        """
        # In a real implementation, this would fetch the child's grades from storage
        # For now, we'll return a placeholder response
        child = next((c for c in self._children if c['id'] == child_id), None)
        if not child:
            return {'error': 'Child not found'}
            
        # This would come from the actual student record
        return {
            'child_id': child_id,
            'child_name': child['name'],
            'grades': {
                'Math': [
                    {'assignment': 'Homework 1', 'grade': 'A', 'date': '2023-10-15'},
                    {'assignment': 'Quiz 1', 'grade': 'B+', 'date': '2023-10-22'}
                ],
                'Science': [
                    {'assignment': 'Lab Report', 'grade': 'A', 'date': '2023-10-18'}
                ]
            },
            'gpa': 3.75,
            'last_updated': datetime.now().isoformat()
        }
    
    def view_child_assignments(self, child_id: str, status: str = 'pending') -> Dict[str, Any]:
        """View a child's assignments.
        
        Args:
            child_id: ID of the child
            status: Filter by status ('pending', 'completed', 'overdue')
            
        Returns:
            Dict with child's assignment information
        """
        # In a real implementation, this would fetch the child's assignments from storage
        # For now, we'll return a placeholder response
        child = next((c for c in self._children if c['id'] == child_id), None)
        if not child:
            return {'error': 'Child not found'}
            
        # Update last checked time
        child['last_checked'] = datetime.now().isoformat()
        
        # This would come from the actual student record
        return {
            'child_id': child_id,
            'child_name': child['name'],
            'assignments': [
                {
                    'id': 'assgn_001',
                    'title': 'Math Homework',
                    'subject': 'Math',
                    'due_date': '2023-11-05',
                    'status': 'pending',
                    'description': 'Complete exercises 1-10 on page 45.'
                },
                {
                    'id': 'assgn_002',
                    'title': 'Science Project',
                    'subject': 'Science',
                    'due_date': '2023-11-10',
                    'status': 'in_progress',
                    'description': 'Work on the solar system model.'
                }
            ],
            'last_updated': datetime.now().isoformat()
        }
    
    def update_notification_preferences(self, **preferences) -> Dict[str, Any]:
        """Update notification preferences.
        
        Args:
            **preferences: Key-value pairs of notification types and their enabled status
            
        Returns:
            Dict with updated preferences
        """
        for pref, enabled in preferences.items():
            if pref in self._notification_preferences:
                self._notification_preferences[pref] = bool(enabled)
                
        return self.get_notification_preferences()
    
    def get_notification_preferences(self) -> Dict[str, bool]:
        """Get current notification preferences."""
        return self._notification_preferences
    
    def get_profile(self) -> Dict[str, Any]:
        """Get the parent's profile with additional parent-specific information."""
        base_profile = super().get_profile()
        base_profile.update({
            'children_count': len(self._children),
            'notification_preferences': self._notification_preferences,
            'last_checked': max(
                [child['last_checked'] for child in self._children], 
                default='Never'
            )
        })
        return base_profile
