from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from ..models.grade import Grade, GradeType
from .base import BaseRepository

class GradeRepository(BaseRepository[Grade]):
    """Repository for managing Grade entities."""
    
    def _get_key(self, item: Grade) -> str:
        """Get the unique key for a grade (its ID)."""
        return item._id
    
    def get_student_grades(self, 
                          student_id: str, 
                          subject: Optional[str] = None,
                          grade_type: Optional[GradeType] = None) -> List[Grade]:
        """Get all grades for a specific student, with optional filters."""
        grades = [g for g in self.get_all() if g._student_id == student_id]
        
        if subject:
            grades = [g for g in grades if g._subject.lower() == subject.lower()]
            
        if grade_type:
            grades = [g for g in grades if g._type == grade_type]
            
        return sorted(grades, key=lambda x: x._created_at, reverse=True)
    
    def get_class_grades(self, 
                        class_id: str, 
                        subject: Optional[str] = None,
                        grade_type: Optional[GradeType] = None) -> Dict[str, List[Grade]]:
        """Get all grades for a specific class, organized by student."""
        # In a real implementation, we would have a way to get students by class
        # For now, we'll assume we can get this information from the grade metadata
        grades = [g for g in self.get_all() if g.get_metadata('class_id') == class_id]
        
        if subject:
            grades = [g for g in grades if g._subject.lower() == subject.lower()]
            
        if grade_type:
            grades = [g for g in grades if g._type == grade_type]
            
        # Group by student
        result = {}
        for grade in grades:
            student_id = grade._student_id
            if student_id not in result:
                result[student_id] = []
            result[student_id].append(grade)
            
        # Sort each student's grades by date
        for student_id in result:
            result[student_id].sort(key=lambda x: x._created_at, reverse=True)
            
        return result
    
    def get_subject_statistics(self, subject: str) -> Dict[str, Any]:
        """Get statistics for a specific subject across all students."""
        subject_grades = [g for g in self.get_all() if g._subject.lower() == subject.lower()]
        
        if not subject_grades:
            return {}
            
        percentages = [g.percentage for g in subject_grades]
        return {
            'subject': subject,
            'average_grade': sum(percentages) / len(percentages),
            'highest_grade': max(percentages),
            'lowest_grade': min(percentages),
            'total_grades': len(percentages),
            'grade_distribution': self._calculate_grade_distribution(percentages)
        }
    
    def _calculate_grade_distribution(self, percentages: List[float]) -> Dict[str, int]:
        """Calculate the distribution of letter grades."""
        distribution = {
            'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0
        }
        
        for pct in percentages:
            if pct >= 90:
                distribution['A'] += 1
            elif pct >= 80:
                distribution['B'] += 1
            elif pct >= 70:
                distribution['C'] += 1
            elif pct >= 60:
                distribution['D'] += 1
            else:
                distribution['F'] += 1
                
        return distribution
    
    def get_student_progress(self, 
                           student_id: str, 
                           subject: Optional[str] = None) -> Dict[str, Any]:
        """Get a student's progress, including trends over time."""
        grades = self.get_student_grades(student_id, subject)
        
        if not grades:
            return {}
            
        # Calculate statistics
        percentages = [g.percentage for g in grades]
        gpa_points = [g.gpa_points for g in grades]
        
        # Group by subject if no specific subject is provided
        if not subject:
            by_subject = {}
            for grade in grades:
                if grade._subject not in by_subject:
                    by_subject[grade._subject] = []
                by_subject[grade._subject].append(grade)
                
            subject_stats = {}
            for subj, subj_grades in by_subject.items():
                subj_percentages = [g.percentage for g in subj_grades]
                subject_stats[subj] = {
                    'average': sum(subj_percentages) / len(subj_percentages),
                    'count': len(subj_percentages),
                    'latest_grade': subj_grades[0].letter_grade if subj_grades else None
                }
        else:
            subject_stats = None
        
        # Calculate trend (simple linear regression)
        trend = "stable"
        if len(grades) >= 2:
            # Simple trend calculation: compare first and last grades
            if percentages[0] > percentages[-1] + 5:  # 5% threshold
                trend = "decreasing"
            elif percentages[-1] > percentages[0] + 5:
                trend = "increasing"
        
        return {
            'student_id': student_id,
            'subject': subject or 'all',
            'average_grade': sum(percentages) / len(percentages),
            'gpa': sum(gpa_points) / len(gpa_points) if gpa_points else 0,
            'total_grades': len(grades),
            'trend': trend,
            'subject_stats': subject_stats,
            'recent_grades': [{
                'subject': g._subject,
                'type': g._type.value,
                'score': g._score,
                'max_score': g._max_score,
                'percentage': g.percentage,
                'letter_grade': g.letter_grade,
                'date': g._created_at.strftime('%Y-%m-%d')
            } for g in grades[:5]]  # Most recent 5 grades
        }
    
    def get_grade_trends(self, 
                        student_id: str, 
                        subject: str,
                        days: int = 90) -> Dict[str, Any]:
        """Get grade trends over time for a student in a subject."""
        cutoff_date = datetime.now() - timedelta(days=days)
        grades = [
            g for g in self.get_student_grades(student_id, subject)
            if g._created_at >= cutoff_date
        ]
        
        if not grades:
            return {}
            
        # Group by date and calculate daily averages
        daily_grades = {}
        for grade in grades:
            date_str = grade._created_at.strftime('%Y-%m-%d')
            if date_str not in daily_grades:
                daily_grades[date_str] = []
            daily_grades[date_str].append(grade.percentage)
            
        # Calculate daily averages
        trend_data = []
        for date_str, percentages in sorted(daily_grades.items()):
            trend_data.append({
                'date': date_str,
                'average': sum(percentages) / len(percentages),
                'count': len(percentages)
            })
            
        return {
            'student_id': student_id,
            'subject': subject,
            'period_days': days,
            'start_date': min(daily_grades.keys()) if daily_grades else None,
            'end_date': max(daily_grades.keys()) if daily_grades else None,
            'data_points': trend_data,
            'overall_average': sum(g.percentage for g in grades) / len(grades) if grades else 0,
            'grade_trend': self._calculate_trend(trend_data) if trend_data else 'insufficient_data'
        }
    
    def _calculate_trend(self, trend_data: List[Dict]) -> str:
        """Calculate the overall trend from trend data."""
        if len(trend_data) < 2:
            return 'insufficient_data'
            
        first = trend_data[0]['average']
        last = trend_data[-1]['average']
        
        if last > first + 5:  # 5% threshold
            return 'improving'
        elif last < first - 5:
            return 'declining'
        return 'stable'
