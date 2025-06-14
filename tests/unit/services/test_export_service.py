"""Unit tests for export_service.py"""
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from eduplatform.services.export_service import ExportService
from eduplatform.models.user import Student, Teacher, Admin, Parent
from eduplatform.models.assignment import Assignment
from eduplatform.models.grade import Grade, GradeType
from eduplatform.models.notification import Notification, NotificationType


class TestExportService(unittest.TestCase):
    """Test cases for ExportService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock services
        self.mock_auth_service = MagicMock()
        self.mock_assignment_service = MagicMock()
        self.mock_grade_service = MagicMock()
        
        # Initialize service with mock dependencies
        self.service = ExportService(
            auth_service=self.mock_auth_service,
            assignment_service=self.mock_assignment_service,
            grade_service=self.mock_grade_service
        )
        
        # Set up test data
        self.test_student = Student(
            user_id="student1",
            full_name="Test Student",
            email="student@example.com",
            password_hash="hashed_password",
            role="student",
            grade=10,
            subjects={"Math", "Science"}
        )
        
        self.test_teacher = Teacher(
            user_id="teacher1",
            full_name="Test Teacher",
            email="teacher@example.com",
            password_hash="hashed_password",
            role="teacher",
            subjects={"Math"},
            is_homeroom_teacher=True
        )
        
        self.test_admin = Admin(
            user_id="admin1",
            full_name="Test Admin",
            email="admin@example.com",
            password_hash="hashed_password",
            role="admin"
        )
        
        self.test_assignment = Assignment(
            assignment_id="assign1",
            title="Test Assignment",
            description="Test Description",
            subject="Math",
            teacher_id="teacher1",
            class_id="class1",
            max_points=100,
            difficulty="medium"
        )
        
        self.test_grade = Grade(
            grade_id="grade1",
            student_id="student1",
            assignment_id="assign1",
            teacher_id="teacher1",
            subject="Math",
            score=85,
            max_score=100,
            type=GradeType.ASSIGNMENT,
            comments="Good job!"
        )
        
        self.test_notification = Notification(
            notification_id="notif1",
            user_id="student1",
            title="Test Notification",
            message="This is a test notification",
            notification_type=NotificationType.ASSIGNMENT_GRADED,
            related_entity_id="assign1",
            related_entity_type="assignment"
        )
        
        # Configure mocks
        self.mock_auth_service.user_repo.get.side_effect = lambda x: {
            "student1": self.test_student,
            "teacher1": self.test_teacher,
            "admin1": self.test_admin
        }.get(x)
        
        self.mock_assignment_service.get_student_assignments.return_value = [
            {"id": "assign1", "title": "Test Assignment", "status": "submitted"}
        ]
        
        self.mock_grade_service.get_student_grades.return_value = [
            {"id": "grade1", "subject": "Math", "score": 85, "max_score": 100}
        ]
        
        self.mock_auth_service.notification_repo.get_user_notifications.return_value = [
            self.test_notification
        ]
        
        # Create temp directory for exports
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests."""
        # Clean up any created files
        for root, _, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            os.rmdir(root)
    
    def test_export_user_data(self):
        """Test exporting user data."""
        # Test
        result = self.service.export_user_data(
            user_id="student1",
            output_dir=self.temp_dir,
            format='xlsx'
        )
        
        # Verify
        self.assertIn('user_info', result)
        self.assertIn('assignments', result)
        self.assertIn('grades', result)
        self.assertIn('notifications', result)
        self.assertIn('manifest', result)
        
        # Check if files were created
        for file_path in result.values():
            if file_path and os.path.exists(file_path):
                self.assertTrue(os.path.isfile(file_path))
    
    def test_export_class_data(self):
        """Test exporting class data."""
        # Configure mocks for class data
        self.mock_auth_service.user_repo.get_users_by_role.return_value = [self.test_student]
        self.mock_assignment_service.get_assignments_by_class.return_value = [self.test_assignment]
        
        # Test
        result = self.service.export_class_data(
            class_id="class1",
            output_dir=self.temp_dir,
            format='xlsx'
        )
        
        # Verify
        self.assertIn('students', result)
        self.assertIn('assignments', result)
        self.assertIn('grades', result)
        self.assertIn('manifest', result)
        
        # Check if files were created
        for file_path in result.values():
            if file_path and os.path.exists(file_path):
                self.assertTrue(os.path.isfile(file_path))
    
    def test_export_school_data(self):
        """Test exporting all school data."""
        # Configure mocks for school data
        self.mock_auth_service.user_repo.get_all.return_value = [
            self.test_student, 
            self.test_teacher, 
            self.test_admin
        ]
        
        self.mock_assignment_service.get_all_assignments.return_value = [self.test_assignment]
        
        # Test
        result = self.service.export_school_data(
            output_dir=self.temp_dir,
            format='xlsx'
        )
        
        # Verify
        self.assertIn('students', result)
        self.assertIn('teachers', result)
        self.assertIn('parents', result)
        self.assertIn('admins', result)
        self.assertIn('assignments', result)
        self.assertIn('grades', result)
        self.assertIn('manifest', result)
        
        # Check if files were created
        for file_path in result.values():
            if file_path and os.path.exists(file_path):
                self.assertTrue(os.path.isfile(file_path))
    
    @patch('eduplatform.services.export_service.datetime')
    def test_export_with_timestamp(self, mock_datetime):
        """Test that exports include timestamps in filenames."""
        # Mock datetime to return a fixed value
        from datetime import datetime
        fixed_time = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_time
        
        # Test
        result = self.service.export_user_data(
            user_id="student1",
            output_dir=self.temp_dir,
            format='xlsx'
        )
        
        # Verify timestamp is in the path
        timestamp = fixed_time.strftime("%Y%m%d_%H%M%S")
        self.assertIn(timestamp, result['manifest'])


if __name__ == '__main__':
    unittest.main()
