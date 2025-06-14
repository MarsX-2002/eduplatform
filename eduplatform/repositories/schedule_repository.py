from typing import Dict, List, Optional, Any, Set, Tuple, Union
from datetime import datetime, time, date, timedelta
from ..models.schedule import Schedule, Weekday
from .base import BaseRepository

class ScheduleRepository(BaseRepository[Schedule]):
    """Repository for managing Schedule entities."""
    
    def _get_key(self, item: Schedule) -> str:
        """Get the unique key for a schedule (its ID)."""
        return item._id
    
    def get_schedule_for_class(self, class_id: str) -> Optional[Schedule]:
        """Get the schedule for a specific class."""
        return next((s for s in self.get_all() if s._class_id == class_id), None)
    
    def get_teacher_schedule(self, teacher_id: str) -> List[Dict]:
        """Get the schedule for a specific teacher across all classes."""
        result = {day.value: [] for day in Weekday}
        
        for schedule in self.get_all():
            for day, sessions in schedule._schedule.items():
                for session in sessions:
                    if session['teacher_id'] == teacher_id:
                        result[day].append({
                            'class_id': schedule._class_id,
                            'subject': session['subject'],
                            'start_time': session['start_time'],
                            'end_time': session['end_time'],
                            'room': session.get('room', '')
                        })
        
        # Sort each day's sessions by start time
        for day in result:
            result[day].sort(key=lambda x: x['start_time'])
            
        return result
    
    def get_student_schedule(self, student_id: str, class_id: str) -> Dict:
        """Get the schedule for a specific student in a class."""
        schedule = self.get_schedule_for_class(class_id)
        if not schedule:
            return {}
            
        # In a real implementation, we would check if the student is enrolled in the class
        # For now, we'll just return the class schedule
        return schedule.to_dict()
    
    def get_classes_on_day(self, day: Union[Weekday, str], time_slot: Optional[time] = None) -> List[Dict]:
        """Get all classes scheduled on a specific day, optionally filtered by time.
        
        Args:
            day: Day of the week
            time_slot: Optional time to check for overlapping sessions
            
        Returns:
            List of class sessions matching the criteria
        """
        if isinstance(day, str):
            day = Weekday(day.lower())
            
        result = []
        
        for schedule in self.get_all():
            for session in schedule._schedule.get(day.value, []):
                if time_slot:
                    # Check if the time slot overlaps with the session
                    start = datetime.strptime(session['start_time'], '%H:%M').time()
                    end = datetime.strptime(session['end_time'], '%H:%M').time()
                    
                    if start <= time_slot < end:
                        result.append({
                            'class_id': schedule._class_id,
                            'subject': session['subject'],
                            'teacher_id': session['teacher_id'],
                            'start_time': session['start_time'],
                            'end_time': session['end_time'],
                            'room': session.get('room', '')
                        })
                else:
                    result.append({
                        'class_id': schedule._class_id,
                        'subject': session['subject'],
                        'teacher_id': session['teacher_id'],
                        'start_time': session['start_time'],
                        'end_time': session['end_time'],
                        'room': session.get('room', '')
                    })
                    
        # Sort by start time
        result.sort(key=lambda x: x['start_time'])
        return result
    
    def get_teacher_availability(self, teacher_id: str, day: Union[Weekday, str]) -> List[Dict]:
        """Get available time slots for a teacher on a specific day."""
        if isinstance(day, str):
            day = Weekday(day.lower())
            
        # Get all scheduled sessions for the teacher on this day
        scheduled_slots = []
        for schedule in self.get_all():
            for session in schedule._schedule.get(day.value, []):
                if session['teacher_id'] == teacher_id:
                    scheduled_slots.append({
                        'start': datetime.strptime(session['start_time'], '%H:%M').time(),
                        'end': datetime.strptime(session['end_time'], '%H:%M').time()
                    })
        
        # Sort scheduled slots by start time
        scheduled_slots.sort(key=lambda x: x['start'])
        
        # Define work hours (8 AM to 5 PM)
        work_start = time(8, 0)
        work_end = time(17, 0)
        
        # Find available slots
        available_slots = []
        current_time = work_start
        
        for slot in scheduled_slots:
            if current_time < slot['start']:
                available_slots.append({
                    'start': current_time.strftime('%H:%M'),
                    'end': slot['start'].strftime('%H:%M')
                })
            current_time = slot['end']
            
        # Add remaining time after last session
        if current_time < work_end:
            available_slots.append({
                'start': current_time.strftime('%H:%M'),
                'end': work_end.strftime('%H:%M')
            })
            
        return available_slots
    
    def find_available_room(self, 
                          day: Union[Weekday, str], 
                          start_time: time, 
                          end_time: time,
                          exclude_rooms: Optional[List[str]] = None) -> Optional[str]:
        """Find an available room at the specified time.
        
        Args:
            day: Day of the week
            start_time: Start time of the desired slot
            end_time: End time of the desired slot
            exclude_rooms: List of room IDs to exclude from the search
            
        Returns:
            Available room ID, or None if no room is available
        """
        if isinstance(day, str):
            day = Weekday(day.lower())
            
        if exclude_rooms is None:
            exclude_rooms = []
            
        # In a real implementation, we would have a list of all available rooms
        # For this example, we'll simulate a few rooms
        all_rooms = ["Room 101", "Room 102", "Room 103", "Room 201", "Room 202", "Lab 1"]
        available_rooms = set(all_rooms) - set(exclude_rooms)
        
        # Check each room for availability
        for room in available_rooms:
            room_available = True
            
            for schedule in self.get_all():
                for session in schedule._schedule.get(day.value, []):
                    if session.get('room') == room:
                        session_start = datetime.strptime(session['start_time'], '%H:%M').time()
                        session_end = datetime.strptime(session['end_time'], '%H:%M').time()
                        
                        # Check for time overlap
                        if not (end_time <= session_start or start_time >= session_end):
                            room_available = False
                            break
                            
                if not room_available:
                    break
                    
            if room_available:
                return room
                
        return None
    
    def get_upcoming_classes(self, days_ahead: int = 7) -> List[Dict]:
        """Get all classes scheduled in the next N days."""
        today = date.today()
        result = []
        
        for i in range(days_ahead + 1):
            current_date = today + timedelta(days=i)
            day_of_week = Weekday(current_date.strftime('%A').lower())
            
            # Get all classes for this day
            classes = self.get_classes_on_day(day_of_week)
            
            for class_info in classes:
                result.append({
                    'date': current_date.isoformat(),
                    'day': day_of_week.value,
                    'class_id': class_info['class_id'],
                    'subject': class_info['subject'],
                    'teacher_id': class_info['teacher_id'],
                    'start_time': class_info['start_time'],
                    'end_time': class_info['end_time'],
                    'room': class_info.get('room', '')
                })
        
        # Sort by date and time
        result.sort(key=lambda x: (x['date'], x['start_time']))
        return result
    
    def get_conflicts(self, 
                    teacher_id: str, 
                    day: Union[Weekday, str], 
                    start_time: time, 
                    end_time: time,
                    exclude_class_id: Optional[str] = None) -> List[Dict]:
        """Find any scheduling conflicts for the given criteria.
        
        Args:
            teacher_id: ID of the teacher
            day: Day of the week
            start_time: Proposed start time
            end_time: Proposed end time
            exclude_class_id: Optional class ID to exclude from conflict check
            
        Returns:
            List of conflicting sessions
        """
        if isinstance(day, str):
            day = Weekday(day.lower())
            
        conflicts = []
        
        for schedule in self.get_all():
            # Skip the class we might be updating
            if exclude_class_id and schedule._class_id == exclude_class_id:
                continue
                
            for session in schedule._schedule.get(day.value, []):
                if session['teacher_id'] == teacher_id:
                    session_start = datetime.strptime(session['start_time'], '%H:%M').time()
                    session_end = datetime.strptime(session['end_time'], '%H:%M').time()
                    
                    # Check for time overlap
                    if not (end_time <= session_start or start_time >= session_end):
                        conflicts.append({
                            'class_id': schedule._class_id,
                            'subject': session['subject'],
                            'teacher_id': teacher_id,
                            'existing_start': session_start.strftime('%H:%M'),
                            'existing_end': session_end.strftime('%H:%M'),
                            'conflict_start': start_time.strftime('%H:%M'),
                            'conflict_end': end_time.strftime('%H:%M')
                        })
                        
        return conflicts
