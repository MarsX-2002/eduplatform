from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from collections import defaultdict
import statistics

from ..models.grade import Grade, GradeType
from ..models.notification import Notification, NotificationType, NotificationPriority
from ..repositories.grade_repository import GradeRepository
from ..repositories.user_repository import UserRepository
from ..repositories.notification_repository import NotificationRepository

class GradeService:
    """Service for handling grade-related operations."""
    
    def __init__(self, 
                 grade_repo: GradeRepository,
                 user_repo: UserRepository,
                 notification_repo: NotificationRepository):
        """Initialize the grade service with required repositories."""
        self.grade_repo = grade_repo
        self.user_repo = user_repo
        self.notification_repo = notification_repo
    
    def record_grade(self,
                    student_id: str,
                    subject: str,
                    grade_type: Union[str, GradeType],
                    score: float,
                    teacher_id: str,
                    max_score: float = 100.0,
                    assignment_id: Optional[str] = None,
                    comments: str = '') -> Grade:
        """Record a new grade for a student.
        
        Args:
            student_id: ID of the student
            subject: Subject the grade is for
            grade_type: Type of grade (e.g., 'assignment', 'exam')
            score: Numeric score
            teacher_id: ID of the teacher recording the grade
            max_score: Maximum possible score (default: 100.0)
            assignment_id: Optional ID of the related assignment
            comments: Optional comments about the grade
            
        Returns:
            The created Grade object
            
        Raises:
            ValueError: If validation fails
        """
        if score < 0 or score > max_score:
            raise ValueError(f"Score must be between 0 and {max_score}")
            
        if isinstance(grade_type, str):
            grade_type = GradeType(grade_type.upper())
            
        # Create the grade record
        grade = Grade(
            student_id=student_id,
            subject=subject,
            grade_type=grade_type,
            score=score,
            max_score=max_score,
            teacher_id=teacher_id,
            assignment_id=assignment_id,
            comments=comments
        )
        
        # Save to repository
        self.grade_repo.add(grade)
        
        # Notify student and parents
        self._notify_grade_recorded(grade)
        
        return grade
    
    def _notify_grade_recorded(self, grade: Grade) -> None:
        """Send notifications about a newly recorded grade."""
        student = self.user_repo.get(grade._student_id)
        teacher = self.user_repo.get(grade._teacher_id)
        
        if not student or not teacher:
            return
            
        # Notify student
        self.notification_repo.create_notification(
            recipient_id=student._id,
            title=f"New Grade in {grade._subject}",
            message=f"You received {grade.percentage}% on a {grade._type.value} in {grade._subject}.",
            notification_type=NotificationType.GRADE.value,
            priority=NotificationPriority.NORMAL,
            related_entity_id=grade._id,
            related_entity_type='grade',
            metadata={
                'subject': grade._subject,
                'score': grade._score,
                'max_score': grade._max_score,
                'percentage': grade.percentage,
                'letter_grade': grade.letter_grade,
                'type': grade._type.value,
                'teacher_name': teacher._full_name,
                'recorded_at': grade._created_at.isoformat()
            }
        )
        
        # Notify parents if student is a minor
        if hasattr(student, '_parent_ids') and student._parent_ids:
            for parent_id in student._parent_ids:
                self.notification_repo.create_notification(
                    recipient_id=parent_id,
                    title=f"Grade Update for {student._full_name}",
                    message=f"{student._first_name} received {grade.percentage}% on a {grade._type.value} in {grade._subject}.",
                    notification_type=NotificationType.GRADE.value,
                    priority=NotificationPriority.NORMAL,
                    related_entity_id=grade._id,
                    related_entity_type='grade',
                    metadata={
                        'student_id': student._id,
                        'student_name': student._full_name,
                        'subject': grade._subject,
                        'score': grade._score,
                        'max_score': grade._max_score,
                        'percentage': grade.percentage,
                        'letter_grade': grade.letter_grade,
                        'type': grade._type.value,
                        'teacher_name': teacher._full_name,
                        'recorded_at': grade._created_at.isoformat()
                    }
                )
    
    def update_grade(self,
                   grade_id: str,
                   score: Optional[float] = None,
                   max_score: Optional[float] = None,
                   comments: Optional[str] = None) -> Optional[Grade]:
        """Update an existing grade.
        
        Args:
            grade_id: ID of the grade to update
            score: New score (if provided)
            max_score: New maximum score (if provided)
            comments: New comments (if provided)
            
        Returns:
            The updated Grade object, or None if not found
            
        Raises:
            ValueError: If validation fails
        """
        grade = self.grade_repo.get(grade_id)
        if not grade:
            return None
            
        if score is not None:
            max = max_score if max_score is not None else grade._max_score
            if score < 0 or score > max:
                raise ValueError(f"Score must be between 0 and {max}")
            grade._score = score
            
        if max_score is not None:
            if max_score <= 0:
                raise ValueError("Maximum score must be greater than 0")
            if score is not None and score > max_score:
                raise ValueError(f"Score cannot be greater than maximum score ({max_score})")
            grade._max_score = max_score
            
        if comments is not None:
            grade._comments = comments
            
        grade._updated_at = datetime.now()
        
        # Save changes
        self.grade_repo.update(grade)
        
        # Notify about grade update
        self._notify_grade_updated(grade)
        
        return grade
    
    def _notify_grade_updated(self, grade: Grade) -> None:
        """Send notifications about a grade update."""
        student = self.user_repo.get(grade._student_id)
        teacher = self.user_repo.get(grade._teacher_id)
        
        if not student or not teacher:
            return
            
        # Notify student
        self.notification_repo.create_notification(
            recipient_id=student._id,
            title=f"Grade Updated in {grade._subject}",
            message=f"Your {grade._type.value} grade in {grade._subject} has been updated to {grade.percentage}%.",
            notification_type=NotificationType.GRADE.value,
            priority=NotificationPriority.NORMAL,
            related_entity_id=grade._id,
            related_entity_type='grade',
            metadata={
                'subject': grade._subject,
                'score': grade._score,
                'max_score': grade._max_score,
                'percentage': grade.percentage,
                'letter_grade': grade.letter_grade,
                'type': grade._type.value,
                'teacher_name': teacher._full_name,
                'updated_at': grade._updated_at.isoformat()
            }
        )
    
    def get_student_grades(self,
                         student_id: str,
                         subject: Optional[str] = None,
                         grade_type: Optional[Union[str, GradeType]] = None,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> List[Dict]:
        """Get grades for a specific student with optional filters.
        
        Args:
            student_id: ID of the student
            subject: Optional subject filter
            grade_type: Optional grade type filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of grade dictionaries with additional metadata
        """
        if isinstance(grade_type, str):
            grade_type = GradeType(grade_type.upper())
            
        grades = self.grade_repo.get_student_grades(
            student_id=student_id,
            subject=subject,
            grade_type=grade_type
        )
        
        # Apply date filters if provided
        if start_date:
            grades = [g for g in grades if g._created_at >= start_date]
        if end_date:
            grades = [g for g in grades if g._created_at <= end_date]
            
        # Convert to dictionary format with additional metadata
        result = []
        for grade in grades:
            teacher = self.user_repo.get(grade._teacher_id)
            result.append({
                'id': grade._id,
                'subject': grade._subject,
                'type': grade._type.value,
                'score': grade._score,
                'max_score': grade._max_score,
                'percentage': grade.percentage,
                'letter_grade': grade.letter_grade,
                'gpa_points': grade.gpa_points,
                'comments': grade._comments,
                'teacher_id': grade._teacher_id,
                'teacher_name': teacher._full_name if teacher else 'Unknown',
                'assignment_id': grade._assignment_id,
                'created_at': grade._created_at.isoformat(),
                'updated_at': grade._updated_at.isoformat() if grade._updated_at else None
            })
            
        # Sort by creation date (newest first)
        result.sort(key=lambda x: x['created_at'], reverse=True)
        return result
    
    def get_class_grades(self,
                       class_id: str,
                       subject: Optional[str] = None,
                       grade_type: Optional[Union[str, GradeType]] = None) -> Dict[str, List[Dict]]:
        """Get grades for all students in a class with optional filters.
        
        Args:
            class_id: ID of the class
            subject: Optional subject filter
            grade_type: Optional grade type filter
            
        Returns:
            Dictionary mapping student IDs to their grade dictionaries
        """
        if isinstance(grade_type, str):
            grade_type = GradeType(grade_type.upper())
            
        grades_by_student = self.grade_repo.get_class_grades(
            class_id=class_id,
            subject=subject,
            grade_type=grade_type
        )
        
        # Convert to dictionary format with additional metadata
        result = {}
        for student_id, grades in grades_by_student.items():
            student = self.user_repo.get(student_id)
            if not student:
                continue
                
            student_grades = []
            for grade in grades:
                teacher = self.user_repo.get(grade._teacher_id)
                student_grades.append({
                    'id': grade._id,
                    'subject': grade._subject,
                    'type': grade._type.value,
                    'score': grade._score,
                    'max_score': grade._max_score,
                    'percentage': grade.percentage,
                    'letter_grade': grade.letter_grade,
                    'gpa_points': grade.gpa_points,
                    'comments': grade._comments,
                    'teacher_id': grade._teacher_id,
                    'teacher_name': teacher._full_name if teacher else 'Unknown',
                    'assignment_id': grade._assignment_id,
                    'created_at': grade._created_at.isoformat(),
                    'updated_at': grade._updated_at.isoformat() if grade._updated_at else None
                })
                
            # Sort by creation date (newest first)
            student_grades.sort(key=lambda x: x['created_at'], reverse=True)
            
            result[student_id] = {
                'student_id': student_id,
                'student_name': student._full_name,
                'grades': student_grades,
                'average_grade': self._calculate_average_grade(grades),
                'gpa': self._calculate_gpa(grades)
            }
            
        return result
    
    def get_student_progress(self,
                           student_id: str,
                           subject: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed progress report for a student.
        
        Args:
            student_id: ID of the student
            subject: Optional subject filter
            
        Returns:
            Dictionary with detailed progress information
        """
        return self.grade_repo.get_student_progress(student_id, subject)
    
    def get_grade_trends(self,
                       student_id: str,
                       subject: str,
                       days: int = 90) -> Dict[str, Any]:
        """Get grade trends over time for a student in a subject.
        
        Args:
            student_id: ID of the student
            subject: Subject to analyze
            days: Number of days to look back
            
        Returns:
            Dictionary with trend data
        """
        return self.grade_repo.get_grade_trends(student_id, subject, days)
    
    def get_subject_statistics(self, subject: str) -> Dict[str, Any]:
        """Get statistics for a specific subject across all students.
        
        Args:
            subject: Subject to analyze
            
        Returns:
            Dictionary with subject statistics
        """
        return self.grade_repo.get_subject_statistics(subject)
    
    def _calculate_average_grade(self, grades: List[Grade]) -> float:
        """Calculate the average grade from a list of grades."""
        if not grades:
            return 0.0
        return sum(g.percentage for g in grades) / len(grades)
    
    def _calculate_gpa(self, grades: List[Grade]) -> float:
        """Calculate GPA from a list of grades."""
        if not grades:
            return 0.0
        return sum(g.gpa_points for g in grades) / len(grades)
    
    def generate_report_card(self, 
                          student_id: str,
                          term: Optional[str] = None) -> Dict[str, Any]:
        """Generate a report card for a student.
        
        Args:
            student_id: ID of the student
            term: Optional term/semester (e.g., 'Fall 2023')
            
        Returns:
            Dictionary with report card data
        """
        # Get all grades for the student
        grades = self.grade_repo.get_student_grades(student_id)
        
        if not grades:
            return {
                'student_id': student_id,
                'term': term or 'Current Term',
                'subjects': [],
                'gpa': 0.0,
                'generated_at': datetime.now().isoformat()
            }
        
        # Group by subject
        subjects = {}
        for grade in grades:
            if grade._subject not in subjects:
                subjects[grade._subject] = []
            subjects[grade._subject].append(grade)
        
        # Calculate subject averages and GPAs
        subject_data = []
        for subject, subject_grades in subjects.items():
            avg_grade = self._calculate_average_grade(subject_grades)
            gpa = self._calculate_gpa(subject_grades)
            
            # Get most recent grade for letter grade
            latest_grade = max(subject_grades, key=lambda g: g._created_at)
            
            subject_data.append({
                'subject': subject,
                'average_grade': avg_grade,
                'letter_grade': latest_grade.letter_grade,
                'gpa': gpa,
                'grade_count': len(subject_grades),
                'latest_grade': {
                    'score': latest_grade._score,
                    'max_score': latest_grade._max_score,
                    'type': latest_grade._type.value,
                    'date': latest_grade._created_at.strftime('%Y-%m-%d')
                }
            })
        
        # Calculate overall GPA
        overall_gpa = self._calculate_gpa(grades)
        
        return {
            'student_id': student_id,
            'term': term or 'Current Term',
            'subjects': subject_data,
            'gpa': overall_gpa,
            'letter_grade': Grade.percentage_to_letter_grade(
                self._calculate_average_grade(grades)
            ),
            'generated_at': datetime.now().isoformat()
        }
