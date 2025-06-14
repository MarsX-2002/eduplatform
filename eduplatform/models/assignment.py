from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum

class AssignmentStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    GRADED = "graded"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class AssignmentDifficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Assignment:
    """Class representing an assignment in the educational platform."""
    
    def __init__(self, 
                 title: str, 
                 description: str, 
                 subject: str,
                 teacher_id: str,
                 class_id: str,
                 due_date: Optional[datetime] = None,
                 max_points: float = 100.0,
                 difficulty: AssignmentDifficulty = AssignmentDifficulty.MEDIUM):
        """Initialize a new assignment.
        
        Args:
            title: Assignment title
            description: Detailed description
            subject: Subject this assignment is for
            teacher_id: ID of the teacher who created the assignment
            class_id: ID of the class this assignment is for
            due_date: Optional due date (defaults to 7 days from creation)
            max_points: Maximum points possible
            difficulty: Assignment difficulty level
        """
        self._id = f"assgn_{len(str(hash(str(datetime.now()))))[-6:]}"
        self._title = title
        self._description = description
        self._subject = subject
        self._teacher_id = teacher_id
        self._class_id = class_id
        self._created_at = datetime.now()
        self._due_date = due_date if due_date else (datetime.now() + timedelta(days=7))
        self._max_points = max(float(max_points))
        self._difficulty = difficulty
        self._status = AssignmentStatus.DRAFT.value
        self._submissions: Dict[str, Dict] = {}  # {student_id: submission_data}
        self._grades: Dict[str, Dict] = {}  # {student_id: grade_data}
        self._attachments: List[Dict] = []  # List of file attachments
    
    @property
    def id(self) -> str:
        """Get the assignment ID."""
        return self._id
    
    @property
    def title(self) -> str:
        """Get the assignment title."""
        return self._title
    
    @property
    def status(self) -> str:
        """Get the current status of the assignment."""
        self._update_status()
        return self._status
    
    def _update_status(self) -> None:
        """Update the status based on current conditions."""
        now = datetime.now()
        
        # If due date has passed and not all submissions are graded
        if now > self._due_date and any(sub.get('status') != 'graded' for sub in self._submissions.values()):
            self._status = AssignmentStatus.OVERDUE.value
        # If any submissions exist but not all are graded
        elif self._submissions and any(sub.get('status') != 'graded' for sub in self._submissions.values()):
            self._status = AssignmentStatus.SUBMITTED.value
        # If all submissions are graded
        elif self._submissions and all(sub.get('status') == 'graded' for sub in self._submissions.values()):
            self._status = AssignmentStatus.GRADED.value
        # If published but no submissions yet
        elif self._status == AssignmentStatus.PUBLISHED.value:
            self._status = AssignmentStatus.IN_PROGRESS.value
    
    def publish(self) -> bool:
        """Publish the assignment to make it visible to students."""
        if self._status == AssignmentStatus.DRAFT.value:
            self._status = AssignmentStatus.PUBLISHED.value
            return True
        return False
    
    def add_submission(self, student_id: str, content: str, attachments: Optional[List[Dict]] = None) -> bool:
        """Add a student's submission for this assignment.
        
        Args:
            student_id: ID of the student submitting
            content: Text content of the submission
            attachments: Optional list of file attachments
            
        Returns:
            bool: True if submission was added, False if already exists or assignment not published
        """
        if self._status == AssignmentStatus.DRAFT.value:
            return False
            
        if student_id in self._submissions:
            return False
            
        self._submissions[student_id] = {
            'content': content,
            'submitted_at': datetime.now(),
            'attachments': attachments or [],
            'status': 'submitted',
            'grade': None,
            'feedback': None
        }
        
        self._update_status()
        return True
    
    def grade_submission(self, student_id: str, grade: float, feedback: str = '') -> bool:
        """Grade a student's submission.
        
        Args:
            student_id: ID of the student
            grade: Numeric grade (0 to max_points)
            feedback: Optional feedback comments
            
        Returns:
            bool: True if graded successfully, False if invalid
        """
        if student_id not in self._submissions:
            return False
            
        # Ensure grade is within valid range
        grade = max(0, min(float(grade), self._max_points))
        
        self._grades[student_id] = {
            'grade': grade,
            'feedback': feedback,
            'graded_at': datetime.now(),
            'graded_by': self._teacher_id
        }
        
        self._submissions[student_id].update({
            'status': 'graded',
            'grade': grade,
            'feedback': feedback
        })
        
        self._update_status()
        return True
    
    def get_submission(self, student_id: str) -> Optional[Dict]:
        """Get a student's submission."""
        return self._submissions.get(student_id)
    
    def get_grade(self, student_id: str) -> Optional[Dict]:
        """Get a student's grade for this assignment."""
        return self._grades.get(student_id)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the assignment."""
        submitted = len(self._submissions)
        graded = sum(1 for s in self._submissions.values() if s.get('status') == 'graded')
        
        return {
            'id': self._id,
            'title': self._title,
            'subject': self._subject,
            'status': self.status,
            'due_date': self._due_date.isoformat(),
            'max_points': self._max_points,
            'difficulty': self._difficulty.value,
            'submissions': submitted,
            'graded': graded,
            'completion_rate': (submitted / len(self._submissions)) * 100 if self._submissions else 0,
            'average_grade': (sum(g.get('grade', 0) for g in self._grades.values()) / len(self._grades)) if self._grades else 0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the assignment to a dictionary."""
        return {
            'id': self._id,
            'title': self._title,
            'description': self._description,
            'subject': self._subject,
            'teacher_id': self._teacher_id,
            'class_id': self._class_id,
            'created_at': self._created_at.isoformat(),
            'due_date': self._due_date.isoformat(),
            'max_points': self._max_points,
            'difficulty': self._difficulty.value,
            'status': self.status,
            'submission_count': len(self._submissions),
            'graded_count': sum(1 for s in self._submissions.values() if s.get('status') == 'graded')
        }
