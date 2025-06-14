"""
Service for exporting application data to various formats.
"""
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Type, TypeVar, cast
from pathlib import Path

from ..models.user import User
from ..models.student import Student
from ..models.teacher import Teacher
from ..models.parent import Parent
from ..models.admin import Admin
from ..models.assignment import Assignment, AssignmentStatus
from ..models.grade import Grade, GradeType
from ..models.notification import Notification, NotificationType
from ..utils.export_utils import ExportUtils
from .auth_service import AuthService
from .assignment_service import AssignmentService
from .grade_service import GradeService

class ExportService:
    """Service for exporting application data to various formats."""
    
    def __init__(self, 
                 auth_service: AuthService,
                 assignment_service: AssignmentService,
                 grade_service: GradeService):
        """Initialize the export service with required services."""
        self.auth_service = auth_service
        self.assignment_service = assignment_service
        self.grade_service = grade_service
        self.export_utils = ExportUtils()
    
    def export_user_data(self, 
                        user_id: str,
                        output_dir: str = 'exports',
                        format: str = 'xlsx') -> Dict[str, str]:
        """Export all data for a specific user.
        
        Args:
            user_id: ID of the user to export data for
            output_dir: Directory to save exported files
            format: Export format ('xlsx', 'csv', or 'sqlite')
            
        Returns:
            Dict with paths to exported files
            
        Raises:
            ValueError: If user not found or export fails
        """
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Get user data
        user = self.auth_service.user_repo.get(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"{user._full_name.replace(' ', '_')}_{timestamp}"
        
        # Prepare export data
        export_data = {
            'user_info': self._prepare_user_info(user),
            'assignments': self._prepare_user_assignments(user_id),
            'grades': self._prepare_user_grades(user_id),
            'notifications': self._prepare_user_notifications(user_id)
        }
        
        # Export to specified format
        result = {}
        for data_type, data in export_data.items():
            if not data:
                continue
                
            filename = f"{base_filename}_{data_type}.{format}"
            output_path = os.path.join(output_dir, filename)
            
            try:
                exported_path = self.export_utils.export_data(
                    data=data,
                    output_path=output_path,
                    format=format,
                    sheet_name=data_type.replace('_', ' ').title()
                )
                result[data_type] = exported_path
            except Exception as e:
                # Continue with other exports if one fails
                print(f"Warning: Failed to export {data_type}: {str(e)}")
                continue
        
        # Create a manifest file
        manifest = {
            'export': {
                'user_id': user_id,
                'user_name': user._full_name,
                'timestamp': timestamp,
                'exported_data': list(result.keys()),
                'file_paths': result
            }
        }
        
        # Save manifest
        manifest_path = os.path.join(output_dir, f"{base_filename}_manifest.json")
        with open(manifest_path, 'w') as f:
            import json
            json.dump(manifest, f, indent=2)
        
        result['manifest'] = manifest_path
        return result
    
    def export_class_data(self,
                         class_id: str,
                         output_dir: str = 'exports',
                         format: str = 'xlsx') -> Dict[str, str]:
        """Export data for an entire class.
        
        Args:
            class_id: ID of the class to export data for
            output_dir: Directory to save exported files
            format: Export format ('xlsx', 'csv', or 'sqlite')
            
        Returns:
            Dict with paths to exported files
            
        Raises:
            ValueError: If class not found or export fails
        """
        # In a real implementation, we would get all students in the class
        # For this example, we'll just get all users and filter by role
        users = self.auth_service.user_repo.get_all()
        students = [u for u in users if isinstance(u, Student)]
        
        if not students:
            raise ValueError(f"No students found in class {class_id}")
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"class_{class_id}_{timestamp}"
        
        # Prepare class data
        class_data = {
            'students': [],
            'assignments': [],
            'grades': []
        }
        
        # Get assignments for the class
        assignments = []
        if hasattr(self.assignment_service, 'get_assignments_by_class'):
            assignments = self.assignment_service.get_assignments_by_class(class_id)
        
        # Get grades for each student
        for student in students:
            # Add student info
            student_info = self._prepare_user_info(student)
            student_info['class_id'] = class_id
            class_data['students'].append(student_info)
            
            # Get student grades
            grades = self.grade_service.get_student_grades(student._id)
            for grade in grades:
                grade_record = {
                    'student_id': student._id,
                    'student_name': student._full_name,
                    'subject': grade.get('subject'),
                    'type': grade.get('type'),
                    'score': grade.get('score'),
                    'max_score': grade.get('max_score'),
                    'percentage': grade.get('percentage'),
                    'letter_grade': grade.get('letter_grade'),
                    'comments': grade.get('comments'),
                    'date': grade.get('created_at')
                }
                class_data['grades'].append(grade_record)
        
        # Add assignment data
        for assignment in assignments:
            assignment_data = {
                'assignment_id': getattr(assignment, '_id', ''),
                'title': getattr(assignment, '_title', ''),
                'subject': getattr(assignment, '_subject', ''),
                'due_date': getattr(assignment, '_due_date', ''),
                'max_points': getattr(assignment, '_max_points', 0),
                'difficulty': getattr(assignment, '_difficulty', ''),
                'status': getattr(assignment, '_status', '')
            }
            class_data['assignments'].append(assignment_data)
        
        # Export to specified format
        result = {}
        for data_type, data in class_data.items():
            if not data:
                continue
                
            filename = f"{base_filename}_{data_type}.{format}"
            output_path = os.path.join(output_dir, filename)
            
            try:
                exported_path = self.export_utils.export_data(
                    data=data,
                    output_path=output_path,
                    format=format,
                    sheet_name=data_type.replace('_', ' ').title()
                )
                result[data_type] = exported_path
            except Exception as e:
                # Continue with other exports if one fails
                print(f"Warning: Failed to export {data_type}: {str(e)}")
                continue
        
        # Create a manifest file
        manifest = {
            'export': {
                'class_id': class_id,
                'timestamp': timestamp,
                'exported_data': list(result.keys()),
                'student_count': len(students),
                'assignment_count': len(assignments),
                'file_paths': result
            }
        }
        
        # Save manifest
        manifest_path = os.path.join(output_dir, f"{base_filename}_manifest.json")
        with open(manifest_path, 'w') as f:
            import json
            json.dump(manifest, f, indent=2)
        
        result['manifest'] = manifest_path
        return result
    
    def export_school_data(self,
                          output_dir: str = 'exports',
                          format: str = 'xlsx') -> Dict[str, str]:
        """Export all school data (Admin only).
        
        Args:
            output_dir: Directory to save exported files
            format: Export format ('xlsx', 'csv', or 'sqlite')
            
        Returns:
            Dict with paths to exported files
            
        Raises:
            ValueError: If export fails
        """
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"school_export_{timestamp}"
        
        # Get all data
        users = self.auth_service.user_repo.get_all()
        students = [u for u in users if isinstance(u, Student)]
        teachers = [u for u in users if isinstance(u, Teacher)]
        parents = [u for u in users if isinstance(u, Parent)]
        admins = [u for u in users if isinstance(u, Admin)]
        
        # Prepare data for export
        export_data = {
            'students': [self._prepare_user_info(u) for u in students],
            'teachers': [self._prepare_user_info(u) for u in teachers],
            'parents': [self._prepare_user_info(u) for u in parents],
            'admins': [self._prepare_user_info(u) for u in admins],
        }
        
        # Get assignments and grades if available
        if hasattr(self.assignment_service, 'get_all_assignments'):
            assignments = self.assignment_service.get_all_assignments()
            export_data['assignments'] = [
                self._prepare_assignment_data(a) for a in assignments
            ]
        
        # Get all grades
        all_grades = []
        for student in students:
            grades = self.grade_service.get_student_grades(student._id)
            all_grades.extend(grades)
        export_data['grades'] = all_grades
        
        # Export to specified format
        result = {}
        for data_type, data in export_data.items():
            if not data:
                continue
                
            filename = f"{base_filename}_{data_type}.{format}"
            output_path = os.path.join(output_dir, filename)
            
            try:
                exported_path = self.export_utils.export_data(
                    data=data,
                    output_path=output_path,
                    format=format,
                    sheet_name=data_type.replace('_', ' ').title()
                )
                result[data_type] = exported_path
            except Exception as e:
                # Continue with other exports if one fails
                print(f"Warning: Failed to export {data_type}: {str(e)}")
                continue
        
        # Create a manifest file
        manifest = {
            'export': {
                'type': 'full_school_export',
                'timestamp': timestamp,
                'student_count': len(students),
                'teacher_count': len(teachers),
                'parent_count': len(parents),
                'admin_count': len(admins),
                'assignment_count': len(export_data.get('assignments', [])),
                'grade_count': len(all_grades),
                'exported_data': list(result.keys()),
                'file_paths': result
            }
        }
        
        # Save manifest
        manifest_path = os.path.join(output_dir, f"{base_filename}_manifest.json")
        with open(manifest_path, 'w') as f:
            import json
            json.dump(manifest, f, indent=2)
        
        result['manifest'] = manifest_path
        return result
    
    # Helper methods for data preparation
    
    def _prepare_user_info(self, user: User) -> Dict[str, Any]:
        """Prepare user information for export."""
        if not user:
            return {}
            
        user_data = {
            'id': getattr(user, '_id', ''),
            'full_name': getattr(user, '_full_name', ''),
            'email': getattr(user, '_email', ''),
            'role': getattr(user, '_role', '').value if hasattr(user, '_role') else 'user',
            'created_at': getattr(user, '_created_at', '').isoformat() if hasattr(user, '_created_at') else ''
        }
        
        # Add role-specific fields
        if isinstance(user, Student):
            user_data.update({
                'grade': getattr(user, '_grade', ''),
                'subjects': ', '.join(getattr(user, '_subjects', {}).keys())
            })
        elif isinstance(user, Teacher):
            user_data.update({
                'subjects': ', '.join(getattr(user, '_subjects', [])),
                'classes': ', '.join(getattr(user, '_classes', []))
            })
        elif isinstance(user, Parent):
            children = getattr(user, '_children', [])
            user_data['children_count'] = len(children)
            
        # Add contact information if available
        if hasattr(user, '_phone'):
            user_data['phone'] = user._phone
        if hasattr(user, '_address'):
            user_data['address'] = user._address
            
        return user_data
    
    def _prepare_user_assignments(self, user_id: str) -> List[Dict[str, Any]]:
        """Prepare assignment data for a user."""
        try:
            if hasattr(self.assignment_service, 'get_student_assignments'):
                return self.assignment_service.get_student_assignments(user_id)
            return []
        except Exception:
            return []
    
    def _prepare_user_grades(self, user_id: str) -> List[Dict[str, Any]]:
        """Prepare grade data for a user."""
        try:
            return self.grade_service.get_student_grades(user_id)
        except Exception:
            return []
    
    def _prepare_user_notifications(self, user_id: str) -> List[Dict[str, Any]]:
        """Prepare notification data for a user."""
        try:
            notifications = self.auth_service.notification_repo.get_user_notifications(
                user_id=user_id,
                unread_only=False
            )
            return [{
                'id': n._id,
                'title': n._title,
                'message': n._message,
                'type': n._type.value,
                'priority': n._priority.value,
                'is_read': n._is_read,
                'created_at': n._created_at.isoformat(),
                'related_entity_id': n._related_entity_id,
                'related_entity_type': n._related_entity_type
            } for n in notifications]
        except Exception:
            return []
    
    def _prepare_assignment_data(self, assignment: Assignment) -> Dict[str, Any]:
        """Prepare assignment data for export."""
        if not assignment:
            return {}
            
        return {
            'id': getattr(assignment, '_id', ''),
            'title': getattr(assignment, '_title', ''),
            'description': getattr(assignment, '_description', ''),
            'subject': getattr(assignment, '_subject', ''),
            'teacher_id': getattr(assignment, '_teacher_id', ''),
            'class_id': getattr(assignment, '_class_id', ''),
            'due_date': getattr(assignment, '_due_date', '').isoformat() if hasattr(assignment, '_due_date') else '',
            'max_points': getattr(assignment, '_max_points', 0),
            'difficulty': getattr(assignment, '_difficulty', '').value if hasattr(assignment, '_difficulty') else '',
            'status': getattr(assignment, '_status', '').value if hasattr(assignment, '_status') else '',
            'created_at': getattr(assignment, '_created_at', '').isoformat() if hasattr(assignment, '_created_at') else '',
            'submission_count': len(getattr(assignment, '_submissions', {}))
        }
