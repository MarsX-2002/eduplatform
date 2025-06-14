from typing import Dict, List, Optional, Any
from .user import User, UserRole
from datetime import datetime

class Student(User):
    """Student class representing a student in the educational platform."""
    
    def __init__(self, full_name: str, email: str, password: str, grade: str):
        """Initialize a new student.
        
        Args:
            full_name: Student's full name
            email: Student's email (must be unique)
            password: Student's password (will be hashed)
            grade: Student's grade/class (e.g., '9-A')
        """
        super().__init__(full_name, email, password, UserRole.STUDENT)
        self._grade = grade
        self._subjects: Dict[str, str] = {}  # {subject_name: teacher_id}
        self._assignments: Dict[str, Dict] = {}  # {assignment_id: {status: str, submission: Optional[str]}}
        self._grades: Dict[str, List[Dict]] = {}  # {subject: [{'value': int, 'date': str, 'teacher_id': str, 'comment': str}]}
    
    @property
    def grade(self) -> str:
        """Get the student's grade/class."""
        return self._grade
    
    def enroll_in_subject(self, subject: str, teacher_id: str) -> bool:
        """Enroll the student in a subject.
        
        Args:
            subject: Name of the subject
            teacher_id: ID of the teacher for this subject
            
        Returns:
            bool: True if enrolled successfully, False if already enrolled
        """
        if subject in self._subjects:
            return False
        self._subjects[subject] = teacher_id
        self._grades[subject] = []
        return True
    
    def submit_assignment(self, assignment_id: str, content: str) -> bool:
        """Submit an assignment.
        
        Args:
            assignment_id: ID of the assignment
            content: The assignment content/submission
            
        Returns:
            bool: True if submitted successfully, False if already submitted
        """
        if assignment_id in self._assignments:
            return False
            
        self._assignments[assignment_id] = {
            'status': 'submitted',
            'submission': content,
            'submission_date': datetime.now().isoformat()
        }
        return True
    
    def view_grades(self, subject: Optional[str] = None) -> Dict[str, Any]:
        """View grades, optionally filtered by subject.
        
        Args:
            subject: Optional subject to filter grades by
            
        Returns:
            Dict containing grades information
        """
        if subject:
            return {
                'subject': subject,
                'grades': self._grades.get(subject, []),
                'average': self._calculate_average(subject) if subject in self._grades else None
            }
        
        return {
            'all_grades': self._grades,
            'overall_average': self.calculate_overall_average()
        }
    
    def _calculate_average(self, subject: str) -> float:
        """Calculate the average grade for a specific subject."""
        if subject not in self._grades or not self._grades[subject]:
            return 0.0
            
        grades = [g['value'] for g in self._grades[subject] if 'value' in g]
        return sum(grades) / len(grades) if grades else 0.0
    
    def calculate_overall_average(self) -> float:
        """Calculate the overall average grade across all subjects."""
        if not self._grades:
            return 0.0
            
        subject_averages = [self._calculate_average(subject) for subject in self._grades]
        return sum(subject_averages) / len(subject_averages) if subject_averages else 0.0
    
    def get_profile(self) -> Dict[str, Any]:
        """Get the student's profile with additional student-specific information."""
        base_profile = super().get_profile()
        base_profile.update({
            'grade': self._grade,
            'subjects': list(self._subjects.keys()),
            'assignments_status': {aid: data['status'] for aid, data in self._assignments.items()},
            'gpa': round(self.calculate_overall_average(), 2)
        })
        return base_profile
    
    def receive_grade(self, assignment_id: str, grade: int, teacher_id: str, comment: str = '') -> bool:
        """Receive a grade for an assignment.
        
        Args:
            assignment_id: ID of the assignment
            grade: Grade received (1-5)
            teacher_id: ID of the teacher who graded
            comment: Optional comment from the teacher
            
        Returns:
            bool: True if grade was recorded, False if assignment not found
        """
        if assignment_id not in self._assignments:
            return False
            
        # Find the subject this assignment is for
        # In a real implementation, we'd look this up from the assignment
        # For now, we'll just use   a placeholder
        subject = next((s for s in self._subjects if self._subjects[s] == teacher_id), 'General')
        
        if subject not in self._grades:
            self._grades[subject] = []
            
        self._grades[subject].append({
            'value': grade,
            'date': datetime.now().isoformat(),
            'teacher_id': teacher_id,
            'comment': comment,
            'assignment_id': assignment_id
        })
        
        self._assignments[assignment_id]['status'] = 'graded'
        return True
