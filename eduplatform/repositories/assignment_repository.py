from typing import Dict, List, Optional, Any
from datetime import datetime
from ..models.assignment import Assignment, AssignmentStatus, AssignmentDifficulty
from .base import BaseRepository

class AssignmentRepository(BaseRepository[Assignment]):
    """Repository for managing Assignment entities."""
    
    def _get_key(self, item: Assignment) -> str:
        """Get the unique key for an assignment (its ID)."""
        return item._id
    
    def get_by_teacher(self, teacher_id: str) -> List[Assignment]:
        """Get all assignments created by a specific teacher."""
        return [a for a in self.get_all() if a._teacher_id == teacher_id]
    
    def get_by_class(self, class_id: str, status: Optional[str] = None) -> List[Assignment]:
        """Get all assignments for a specific class, optionally filtered by status."""
        assignments = [a for a in self.get_all() if a._class_id == class_id]
        if status:
            return [a for a in assignments if a.status == status]
        return assignments
    
    def get_by_subject(self, subject: str, status: Optional[str] = None) -> List[Assignment]:
        """Get all assignments for a specific subject, optionally filtered by status."""
        assignments = [a for a in self.get_all() if a._subject.lower() == subject.lower()]
        if status:
            return [a for a in assignments if a.status == status]
        return assignments
    
    def get_due_soon(self, days: int = 7) -> List[Assignment]:
        """Get assignments that are due within the specified number of days."""
        now = datetime.now()
        due_date = now + datetime.timedelta(days=days)
        
        return [
            a for a in self.get_all() 
            if a._status == AssignmentStatus.PUBLISHED.value and 
               now < a._due_date <= due_date
        ]
    
    def get_overdue(self) -> List[Assignment]:
        """Get all overdue assignments."""
        now = datetime.now()
        return [
            a for a in self.get_all() 
            if a._due_date < now and 
               a._status in [AssignmentStatus.PUBLISHED.value, AssignmentStatus.IN_PROGRESS.value]
        ]
    
    def get_by_difficulty(self, difficulty: AssignmentDifficulty) -> List[Assignment]:
        """Get all assignments of a specific difficulty level."""
        return [a for a in self.get_all() if a._difficulty == difficulty]
    
    def get_active_assignments(self) -> List[Assignment]:
        """Get all active (published and not yet due) assignments."""
        now = datetime.now()
        return [
            a for a in self.get_all() 
            if a._status in [AssignmentStatus.PUBLISHED.value, AssignmentStatus.IN_PROGRESS.value] and 
               a._due_date > now
        ]
    
    def get_submissions_summary(self, assignment_id: str) -> Dict[str, Any]:
        """Get a summary of submissions for an assignment."""
        assignment = self.get(assignment_id)
        if not assignment:
            return {}
            
        submissions = assignment._submissions
        total = len(submissions)
        graded = sum(1 for s in submissions.values() if s.get('status') == 'graded')
        
        return {
            'assignment_id': assignment_id,
            'title': assignment._title,
            'total_submissions': total,
            'graded': graded,
            'pending': total - graded,
            'submission_rate': (total / 100) * 100 if hasattr(assignment, '_class_size') and assignment._class_size > 0 else 0,
            'average_grade': sum(s.get('grade', 0) for s in submissions.values() if s.get('grade') is not None) / graded if graded > 0 else 0
        }
    
    def get_teacher_workload(self, teacher_id: str) -> Dict[str, Any]:
        """Get workload statistics for a teacher."""
        teacher_assignments = self.get_by_teacher(teacher_id)
        now = datetime.now()
        
        active = []
        grading_needed = []
        
        for assignment in teacher_assignments:
            if assignment._status in [AssignmentStatus.PUBLISHED.value, AssignmentStatus.IN_PROGRESS.value]:
                active.append(assignment)
                
                # Count ungraded submissions
                ungraded = sum(1 for s in assignment._submissions.values() 
                             if s.get('status') == 'submitted')
                if ungraded > 0:
                    grading_needed.append({
                        'assignment_id': assignment._id,
                        'title': assignment._title,
                        'ungraded_count': ungraded,
                        'due_date': assignment._due_date
                    })
        
        return {
            'total_assignments': len(teacher_assignments),
            'active_assignments': len(active),
            'grading_needed': grading_needed,
            'overdue_grading': len([a for a in active if a._due_date < now])
        }
    
    def search_assignments(self, 
                          query: str = '', 
                          subject: Optional[str] = None,
                          status: Optional[str] = None,
                          teacher_id: Optional[str] = None,
                          class_id: Optional[str] = None) -> List[Assignment]:
        """Search assignments with various filters."""
        results = self.get_all()
        
        if query:
            query = query.lower()
            results = [a for a in results 
                     if query in a._title.lower() or 
                        query in a._description.lower()]
                        
        if subject:
            results = [a for a in results if a._subject.lower() == subject.lower()]
            
        if status:
            results = [a for a in results if a.status == status]
            
        if teacher_id:
            results = [a for a in results if a._teacher_id == teacher_id]
            
        if class_id:
            results = [a for a in results if a._class_id == class_id]
            
        return results
