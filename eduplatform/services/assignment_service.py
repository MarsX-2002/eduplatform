from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from ..models.assignment import Assignment, AssignmentStatus, AssignmentDifficulty
from ..models.grade import Grade, GradeType
from ..models.notification import Notification, NotificationType, NotificationPriority
from ..repositories.assignment_repository import AssignmentRepository
from ..repositories.grade_repository import GradeRepository
from ..repositories.notification_repository import NotificationRepository
from ..repositories.user_repository import UserRepository

class AssignmentService:
    """Service for handling assignment-related operations."""
    
    def __init__(self, 
                 assignment_repo: AssignmentRepository,
                 grade_repo: GradeRepository,
                 user_repo: UserRepository,
                 notification_repo: NotificationRepository):
        """Initialize the assignment service with required repositories."""
        self.assignment_repo = assignment_repo
        self.grade_repo = grade_repo
        self.user_repo = user_repo
        self.notification_repo = notification_repo
    
    def create_assignment(self,
                         teacher_id: str,
                         title: str,
                         description: str,
                         subject: str,
                         class_id: str,
                         due_date: datetime,
                         max_points: float = 100.0,
                         difficulty: Union[str, AssignmentDifficulty] = AssignmentDifficulty.MEDIUM,
                         attachments: Optional[List[Dict]] = None) -> Assignment:
        """Create a new assignment.
        
        Args:
            teacher_id: ID of the teacher creating the assignment
            title: Assignment title
            description: Detailed description
            subject: Subject this assignment is for
            class_id: ID of the class this assignment is for
            due_date: Due date for the assignment
            max_points: Maximum points possible
            difficulty: Difficulty level of the assignment
            attachments: Optional list of file attachments
            
        Returns:
            The created Assignment object
            
        Raises:
            ValueError: If validation fails
        """
        # Validate input
        if due_date < datetime.now():
            raise ValueError("Due date cannot be in the past")
            
        if max_points <= 0:
            raise ValueError("Maximum points must be greater than 0")
            
        if isinstance(difficulty, str):
            difficulty = AssignmentDifficulty(difficulty.lower())
            
        # Create the assignment
        assignment = Assignment(
            title=title,
            description=description,
            subject=subject,
            teacher_id=teacher_id,
            class_id=class_id,
            due_date=due_date,
            max_points=max_points,
            difficulty=difficulty
        )
        
        # Add any attachments
        if attachments:
            for attachment in attachments:
                assignment.add_attachment(attachment)
        
        # Publish the assignment
        assignment.publish()
        
        # Save to repository
        self.assignment_repo.add(assignment)
        
        # Notify students (in a real app, this would be done asynchronously)
        self._notify_students(assignment)
        
        return assignment
    
    def _notify_students(self, assignment: Assignment) -> None:
        """Notify students about a new assignment."""
        # In a real implementation, we would get the list of students in the class
        # For this example, we'll just create a notification for the assignment
        notification = self.notification_repo.create_notification(
            recipient_id=f"class_{assignment._class_id}",  # This would be expanded to individual student IDs
            title=f"New Assignment: {assignment._title}",
            message=f"A new assignment has been posted for {assignment._subject}. Due: {assignment._due_date.strftime('%b %d, %Y')}",
            notification_type=NotificationType.ASSIGNMENT.value,
            priority=NotificationPriority.HIGH,
            related_entity_id=assignment._id,
            related_entity_type='assignment',
            metadata={
                'assignment_id': assignment._id,
                'due_date': assignment._due_date.isoformat(),
                'subject': assignment._subject,
                'max_points': assignment._max_points
            }
        )
    
    def submit_assignment(self,
                         student_id: str,
                         assignment_id: str,
                         content: str,
                         attachments: Optional[List[Dict]] = None,
                         submit_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Submit an assignment.
        
        Args:
            student_id: ID of the student submitting
            assignment_id: ID of the assignment
            content: Text content of the submission
            attachments: Optional list of file attachments
            submit_time: Optional submission time (defaults to now)
            
        Returns:
            Dictionary with submission details
            
        Raises:
            ValueError: If assignment doesn't exist or submission is invalid
        """
        assignment = self.assignment_repo.get(assignment_id)
        if not assignment:
            raise ValueError("Assignment not found")
            
        # Check if submission is on time
        submit_time = submit_time or datetime.now()
        is_late = submit_time > assignment._due_date
        
        # Add submission
        submission_id = assignment.add_submission(
            student_id=student_id,
            content=content,
            submit_time=submit_time,
            is_late=is_late,
            attachments=attachments or []
        )
        
        # Update assignment in repository
        self.assignment_repo.update(assignment)
        
        # Notify teacher
        student = self.user_repo.get(student_id)
        if student:
            self.notification_repo.create_notification(
                recipient_id=assignment._teacher_id,
                title=f"New Submission: {assignment._title}",
                message=f"{student._full_name} has submitted {'late ' if is_late else ''}work for {assignment._title}",
                notification_type=NotificationType.ASSIGNMENT.value,
                priority=NotificationPriority.NORMAL,
                related_entity_id=assignment_id,
                related_entity_type='assignment',
                metadata={
                    'student_id': student_id,
                    'submission_id': submission_id,
                    'is_late': is_late,
                    'submitted_at': submit_time.isoformat()
                }
            )
        
        return {
            'submission_id': submission_id,
            'assignment_id': assignment_id,
            'student_id': student_id,
            'submitted_at': submit_time.isoformat(),
            'is_late': is_late,
            'status': 'submitted'
        }
    
    def grade_assignment(self,
                        teacher_id: str,
                        submission_id: str,
                        grade: float,
                        feedback: str = '',
                        graded_by: Optional[str] = None) -> Dict[str, Any]:
        """Grade a student's assignment submission.
        
        Args:
            teacher_id: ID of the teacher doing the grading
            submission_id: ID of the submission to grade
            grade: Numeric grade (0 to max_points)
            feedback: Optional feedback comments
            graded_by: Optional name of who is grading (defaults to teacher's name)
            
        Returns:
            Dictionary with grading details
            
        Raises:
            ValueError: If submission doesn't exist or grade is invalid
        """
        # In a real implementation, we would look up the submission
        # For this example, we'll assume we can get the assignment from the submission
        assignment = None
        for a in self.assignment_repo.get_all():
            if submission_id in [s['id'] for s in a._submissions.values()]:
                assignment = a
                break
                
        if not assignment:
            raise ValueError("Submission not found")
            
        # Validate grade
        if grade < 0 or grade > assignment._max_points:
            raise ValueError(f"Grade must be between 0 and {assignment._max_points}")
            
        # Get the teacher's name for the feedback
        teacher = self.user_repo.get(teacher_id)
        grader_name = graded_by or (teacher._full_name if teacher else "Teacher")
        
        # Find the submission and update it
        submission = None
        for sub in assignment._submissions.values():
            if sub['id'] == submission_id:
                submission = sub
                break
                
        if not submission:
            raise ValueError("Submission not found")
            
        # Update submission with grade and feedback
        submission['grade'] = grade
        submission['feedback'] = feedback
        submission['graded_by'] = grader_name
        submission['graded_at'] = datetime.now()
        submission['status'] = 'graded'
        
        # Create a grade record
        grade_record = Grade(
            student_id=submission['student_id'],
            subject=assignment._subject,
            grade_type=GradeType.ASSIGNMENT,
            score=grade,
            max_score=assignment._max_points,
            assignment_id=assignment._id,
            teacher_id=teacher_id,
            comments=feedback
        )
        
        # Save grade to repository
        self.grade_repo.add(grade_record)
        
        # Update assignment in repository
        self.assignment_repo.update(assignment)
        
        # Notify student
        self.notification_repo.create_notification(
            recipient_id=submission['student_id'],
            title=f"Grade Posted: {assignment._title}",
            message=f"Your submission for {assignment._title} has been graded: {grade}/{assignment._max_points}",
            notification_type=NotificationType.GRADE.value,
            priority=NotificationPriority.HIGH,
            related_entity_id=assignment._id,
            related_entity_type='assignment',
            metadata={
                'grade': grade,
                'max_grade': assignment._max_points,
                'assignment_title': assignment._title,
                'feedback': feedback
            }
        )
        
        return {
            'submission_id': submission_id,
            'assignment_id': assignment._id,
            'student_id': submission['student_id'],
            'grade': grade,
            'max_grade': assignment._max_points,
            'feedback': feedback,
            'graded_by': grader_name,
            'graded_at': datetime.now().isoformat()
        }
    
    def get_student_assignments(self, 
                              student_id: str, 
                              status: Optional[str] = None,
                              subject: Optional[str] = None) -> List[Dict]:
        """Get assignments for a student with optional filters.
        
        Args:
            student_id: ID of the student
            status: Optional status filter ('pending', 'submitted', 'graded', 'overdue')
            subject: Optional subject filter
            
        Returns:
            List of assignment dictionaries with submission status
        """
        # In a real implementation, we would get the student's class and then assignments
        # For this example, we'll return all assignments with submission status
        now = datetime.now()
        result = []
        
        for assignment in self.assignment_repo.get_all():
            # Skip if subject filter is provided and doesn't match
            if subject and assignment._subject.lower() != subject.lower():
                continue
                
            submission = next(
                (s for s in assignment._submissions.values() if s['student_id'] == student_id),
                None
            )
            
            # Determine status
            assignment_status = 'pending'
            if submission:
                if submission.get('graded_at'):
                    assignment_status = 'graded'
                else:
                    assignment_status = 'submitted'
            elif assignment._due_date < now:
                assignment_status = 'overdue'
                
            # Apply status filter if provided
            if status and assignment_status != status:
                continue
                
            result.append({
                'id': assignment._id,
                'title': assignment._title,
                'subject': assignment._subject,
                'due_date': assignment._due_date.isoformat(),
                'status': assignment_status,
                'submission': submission,
                'max_points': assignment._max_points,
                'difficulty': assignment._difficulty.value,
                'description': assignment._description,
                'teacher_id': assignment._teacher_id,
                'class_id': assignment._class_id
            })
            
        # Sort by due date (ascending)
        result.sort(key=lambda x: x['due_date'])
        return result
    
    def get_teacher_assignments(self, 
                              teacher_id: str,
                              status: Optional[str] = None,
                              class_id: Optional[str] = None) -> List[Dict]:
        """Get assignments created by a teacher with optional filters.
        
        Args:
            teacher_id: ID of the teacher
            status: Optional status filter ('draft', 'published', 'graded', 'overdue')
            class_id: Optional class ID filter
            
        Returns:
            List of assignment dictionaries with submission statistics
        """
        now = datetime.now()
        result = []
        
        for assignment in self.assignment_repo.get_all():
            # Skip if not created by this teacher or doesn't match class filter
            if assignment._teacher_id != teacher_id:
                continue
                
            if class_id and assignment._class_id != class_id:
                continue
                
            # Calculate submission statistics
            total_submissions = len(assignment._submissions)
            graded_submissions = sum(1 for s in assignment._submissions.values() 
                                   if s.get('status') == 'graded')
            
            # Determine status
            assignment_status = 'published'
            if assignment._status == AssignmentStatus.DRAFT.value:
                assignment_status = 'draft'
            elif assignment._due_date < now and total_submissions > graded_submissions:
                assignment_status = 'overdue'
            elif total_submissions == graded_submissions and total_submissions > 0:
                assignment_status = 'graded'
                
            # Apply status filter if provided
            if status and assignment_status != status:
                continue
                
            result.append({
                'id': assignment._id,
                'title': assignment._title,
                'subject': assignment._subject,
                'class_id': assignment._class_id,
                'due_date': assignment._due_date.isoformat(),
                'status': assignment_status,
                'total_submissions': total_submissions,
                'graded_submissions': graded_submissions,
                'submission_rate': (total_submissions / 25) * 100,  # Assuming 25 students per class
                'max_points': assignment._max_points,
                'difficulty': assignment._difficulty.value,
                'created_at': assignment._created_at.isoformat()
            })
            
        # Sort by due date (ascending)
        result.sort(key=lambda x: x['due_date'])
        return result
    
    def get_assignment_details(self, assignment_id: str, user_id: str) -> Optional[Dict]:
        """Get detailed information about an assignment.
        
        Args:
            assignment_id: ID of the assignment
            user_id: ID of the user requesting the details
            
        Returns:
            Dictionary with assignment details, or None if not found
        """
        assignment = self.assignment_repo.get(assignment_id)
        if not assignment:
            return None
            
        # Check if user has permission to view this assignment
        user = self.user_repo.get(user_id)
        if not user:
            return None
            
        # In a real implementation, we would check user roles and permissions
        # For this example, we'll just return basic details
        details = {
            'id': assignment._id,
            'title': assignment._title,
            'description': assignment._description,
            'subject': assignment._subject,
            'class_id': assignment._class_id,
            'teacher_id': assignment._teacher_id,
            'due_date': assignment._due_date.isoformat(),
            'max_points': assignment._max_points,
            'difficulty': assignment._difficulty.value,
            'status': assignment.status,
            'created_at': assignment._created_at.isoformat(),
            'attachments': assignment._attachments
        }
        
        # Add submission info if user is the teacher
        if hasattr(user, '_role') and user._role == 'teacher' and user._id == assignment._teacher_id:
            details['submissions'] = list(assignment._submissions.values())
            details['submission_count'] = len(assignment._submissions)
            details['average_grade'] = self._calculate_average_grade(assignment)
        # Add submission info if user is the student who submitted
        elif hasattr(user, '_role') and user._role == 'student':
            submission = next(
                (s for s in assignment._submissions.values() if s['student_id'] == user_id),
                None
            )
            if submission:
                details['submission'] = submission
                
        return details
    
    def _calculate_average_grade(self, assignment: Assignment) -> float:
        """Calculate the average grade for an assignment."""
        grades = [s.get('grade') for s in assignment._submissions.values() 
                 if s.get('grade') is not None]
        return sum(grades) / len(grades) if grades else 0.0
