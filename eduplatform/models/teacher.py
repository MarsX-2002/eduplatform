from typing import Dict, List, Optional, Any
from .user import User, UserRole
from datetime import datetime, timedelta

class Teacher(User):
    """Teacher class representing a teacher in the educational platform."""
    
    def __init__(self, full_name: str, email: str, password: str):
        """Initialize a new teacher.
        
        Args:
            full_name: Teacher's full name
            email: Teacher's email (must be unique)
            password: Teacher's password (will be hashed)
        """
        super().__init__(full_name, email, password, UserRole.TEACHER)
        self._subjects: List[str] = []
        self._classes: List[str] = []  # List of class/grade names (e.g., ['9-A', '10-B'])
        self._assignments: Dict[str, Dict] = {}  # {assignment_id: assignment_data}
        self._workload: int = 0  # Number of teaching hours per week
    
    def add_subject(self, subject: str) -> bool:
        """Add a subject that the teacher can teach.
        
        Args:
            subject: Name of the subject
            
        Returns:
            bool: True if added, False if already exists
        """
        if subject not in self._subjects:
            self._subjects.append(subject)
            return True
        return False
    
    def add_class(self, class_name: str) -> bool:
        """Add a class/grade that the teacher teaches.
        
        Args:
            class_name: Name of the class/grade (e.g., '9-A')
            
        Returns:
            bool: True if added, False if already exists
        """
        if class_name not in self._classes:
            self._classes.append(class_name)
            return True
        return False
    
    def create_assignment(
        self, 
        title: str, 
        description: str, 
        subject: str, 
        class_name: str,
        days_until_due: int = 7,
        max_points: int = 100
    ) -> Optional[Dict[str, Any]]:
        """Create a new assignment for students.
        
        Args:
            title: Assignment title
            description: Detailed description
            subject: Subject this assignment is for
            class_name: Target class/grade
            days_until_due: Number of days until due date
            max_points: Maximum points possible
            
        Returns:
            Dict with assignment details if created, None if invalid
        """
        if subject not in self._subjects or class_name not in self._classes:
            return None
            
        assignment_id = f"assgn_{len(self._assignments) + 1}_{self._id[-4:]}"
        due_date = (datetime.now() + timedelta(days=days_until_due)).isoformat()
        
        assignment = {
            'id': assignment_id,
            'title': title,
            'description': description,
            'subject': subject,
            'class_name': class_name,
            'teacher_id': self._id,
            'created_at': datetime.now().isoformat(),
            'due_date': due_date,
            'max_points': max_points,
            'status': 'active',
            'submissions': {}  # {student_id: submission_data}
        }
        
        self._assignments[assignment_id] = assignment
        return assignment
    
    def grade_assignment(
        self, 
        assignment_id: str, 
        student_id: str, 
        points: float, 
        comments: str = ''
    ) -> bool:
        """Grade a student's assignment submission.
        
        Args:
            assignment_id: ID of the assignment
            student_id: ID of the student
            points: Points awarded (0 to max_points)
            comments: Optional feedback comments
            
        Returns:
            bool: True if graded successfully, False if invalid
        """
        if assignment_id not in self._assignments:
            return False
            
        assignment = self._assignments[assignment_id]
        
        # Ensure points are within valid range
        points = max(0, min(points, assignment['max_points']))
        
        # Calculate grade (1-5 scale based on percentage)
        percentage = (points / assignment['max_points']) * 100
        grade = self._calculate_grade(percentage)
        
        # Record the grade
        if 'grades' not in assignment:
            assignment['grades'] = {}
            
        assignment['grades'][student_id] = {
            'points': points,
            'grade': grade,
            'comments': comments,
            'graded_at': datetime.now().isoformat()
        }
        
        # In a real implementation, we would update the student's record here
        # For now, we'll just return True to indicate success
        return True
    
    def _calculate_grade(self, percentage: float) -> int:
        """Convert percentage to a 1-5 grade scale."""
        if percentage >= 90:
            return 5
        elif percentage >= 75:
            return 4
        elif percentage >= 60:
            return 3
        elif percentage >= 40:
            return 2
        else:
            return 1
    
    def view_student_progress(self, student_id: str, subject: Optional[str] = None) -> Dict[str, Any]:
        """View a student's progress in the teacher's classes.
        
        Args:
            student_id: ID of the student
            subject: Optional subject to filter by
            
        Returns:
            Dict with student's progress information
        """
        progress = {
            'student_id': student_id,
            'subjects': {},
            'total_assignments': 0,
            'completed_assignments': 0,
            'average_grade': 0.0
        }
        
        # In a real implementation, we would look up the student's actual data
        # For now, we'll return a placeholder response
        
        return progress
    
    def get_profile(self) -> Dict[str, Any]:
        """Get the teacher's profile with additional teacher-specific information."""
        base_profile = super().get_profile()
        base_profile.update({
            'subjects': self._subjects,
            'classes': self._classes,
            'workload_hours': self._workload,
            'active_assignments': len([a for a in self._assignments.values() if a['status'] == 'active'])
        })
        return base_profile
