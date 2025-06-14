from typing import Dict, Optional, Any
from datetime import datetime
from enum import Enum

class GradeType(Enum):
    """Types of grades that can be recorded."""
    ASSIGNMENT = "assignment"
    EXAM = "exam"
    QUIZ = "quiz"
    PARTICIPATION = "participation"
    PROJECT = "project"
    HOMEWORK = "homework"

class Grade:
    """Class representing a grade in the educational platform."""
    
    def __init__(self, 
                 student_id: str, 
                 subject: str, 
                 grade_type: GradeType,
                 score: float,
                 max_score: float = 100.0,
                 assignment_id: Optional[str] = None,
                 teacher_id: Optional[str] = None,
                 comments: str = ''):
        """Initialize a new grade entry.
        
        Args:
            student_id: ID of the student receiving the grade
            subject: Subject the grade is for
            grade_type: Type of grade (assignment, exam, etc.)
            score: Points earned
            max_score: Maximum possible points
            assignment_id: Optional ID of the related assignment
            teacher_id: ID of the teacher who assigned the grade
            comments: Optional comments about the grade
        """
        self._id = f"grade_{len(str(hash(str(datetime.now()))))[-8:]}"
        self._student_id = student_id
        self._subject = subject
        self._type = grade_type
        self._score = float(score)
        self._max_score = float(max_score)
        self._assignment_id = assignment_id
        self._teacher_id = teacher_id
        self._comments = comments
        self._created_at = datetime.now()
        self._updated_at = self._created_at
        self._is_final = False
        self._category = self._determine_category()
    
    def _determine_category(self) -> str:
        """Determine the category of the grade based on its type."""
        if self._type in [GradeType.HOMEWORK, GradeType.ASSIGNMENT, GradeType.PROJECT]:
            return 'assignments'
        elif self._type in [GradeType.QUIZ, GradeType.EXAM]:
            return 'assessments'
        return 'other'
    
    @property
    def percentage(self) -> float:
        """Calculate the grade as a percentage."""
        if self._max_score == 0:
            return 0.0
        return (self._score / self._max_score) * 100
    
    @property
    def letter_grade(self) -> str:
        """Convert the percentage to a letter grade."""
        percentage = self.percentage
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'
    
    @property
    def gpa_points(self) -> float:
        """Convert the letter grade to GPA points (4.0 scale)."""
        letter = self.letter_grade
        if letter == 'A':
            return 4.0
        elif letter == 'B':
            return 3.0
        elif letter == 'C':
            return 2.0
        elif letter == 'D':
            return 1.0
        return 0.0
    
    def update_grade(self, 
                   new_score: Optional[float] = None, 
                   new_comments: Optional[str] = None,
                   is_final: Optional[bool] = None) -> None:
        """Update the grade details.
        
        Args:
            new_score: New score to update (if any)
            new_comments: New comments to add (if any)
            is_final: Whether this grade should be marked as final
        """
        if new_score is not None:
            self._score = float(new_score)
            
        if new_comments is not None:
            if self._comments:
                self._comments += f"\n---\n{new_comments}"
            else:
                self._comments = new_comments
                
        if is_final is not None:
            self._is_final = is_final
            
        self._updated_at = datetime.now()
    
    def to_dict(self, include_student_info: bool = False) -> Dict[str, Any]:
        """Convert the grade to a dictionary.
        
        Args:
            include_student_info: Whether to include student information
            
        Returns:
            Dictionary representation of the grade
        """
        result = {
            'id': self._id,
            'subject': self._subject,
            'type': self._type.value,
            'category': self._category,
            'score': self._score,
            'max_score': self._max_score,
            'percentage': round(self.percentage, 2),
            'letter_grade': self.letter_grade,
            'gpa_points': self.gpa_points,
            'is_final': self._is_final,
            'assignment_id': self._assignment_id,
            'teacher_id': self._teacher_id,
            'created_at': self._created_at.isoformat(),
            'updated_at': self._updated_at.isoformat()
        }
        
        if include_student_info:
            result['student_id'] = self._student_id
            
        if self._comments:
            result['comments'] = self._comments
            
        return result
    
    def get_grade_summary(self) -> Dict[str, Any]:
        """Get a summary of the grade."""
        return {
            'id': self._id,
            'subject': self._subject,
            'type': self._type.value,
            'score': self._score,
            'max_score': self._max_score,
            'percentage': round(self.percentage, 2),
            'letter_grade': self.letter_grade,
            'is_final': self._is_final
        }
    
    @classmethod
    def calculate_class_average(cls, grades: list['Grade']) -> Dict[str, Any]:
        """Calculate class average from a list of grades.
        
        Args:
            grades: List of Grade objects
            
        Returns:
            Dictionary with statistics
        """
        if not grades:
            return {
                'average': 0.0,
                'highest': 0.0,
                'lowest': 0.0,
                'count': 0
            }
            
        percentages = [g.percentage for g in grades]
        return {
            'average': round(sum(percentages) / len(percentages), 2),
            'highest': round(max(percentages), 2),
            'lowest': round(min(percentages), 2),
            'count': len(grades)
        }
