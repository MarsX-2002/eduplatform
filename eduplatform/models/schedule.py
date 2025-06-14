from typing import Dict, List, Optional, Any
from datetime import time, datetime, timedelta
from enum import Enum

class Weekday(Enum):
    """Days of the week for scheduling."""
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

class Schedule:
    """Class representing a schedule for classes in the educational platform."""
    
    def __init__(self, 
                 class_id: str,
                 start_date: datetime,
                 end_date: datetime,
                 schedule_type: str = "weekly"):
        """Initialize a new schedule.
        
        Args:
            class_id: ID of the class this schedule is for
            start_date: When the schedule becomes active
            end_date: When the schedule expires
            schedule_type: Type of schedule (weekly, daily, custom)
        """
        self._id = f"sched_{len(str(hash(str(datetime.now()))))[-8:]}"
        self._class_id = class_id
        self._start_date = start_date
        self._end_date = end_date
        self._type = schedule_type
        self._schedule: Dict[str, List[Dict]] = {
            day.value: [] for day in Weekday
        }
        self._exceptions: List[Dict] = []  # For holidays, special events
        self._last_updated = datetime.now()
    
    def add_class_session(self,
                        subject: str,
                        teacher_id: str,
                        day: Weekday,
                        start_time: time,
                        end_time: time,
                        room: str = "",
                        recurring: bool = True) -> bool:
        """Add a class session to the schedule.
        
        Args:
            subject: Subject being taught
            teacher_id: ID of the teacher
            day: Day of the week
            start_time: Start time
            end_time: End time
            room: Room number/location
            recurring: Whether this is a recurring session
            
        Returns:
            bool: True if added successfully, False if there's a conflict
        """
        if self._has_conflict(day.value, start_time, end_time, teacher_id=teacher_id):
            return False
            
        session = {
            'id': f"sess_{len(str(hash(str(datetime.now()))))[-6:]}",
            'subject': subject,
            'teacher_id': teacher_id,
            'start_time': start_time.strftime('%H:%M'),
            'end_time': end_time.strftime('%H:%M'),
            'room': room,
            'recurring': recurring,
            'created_at': datetime.now().isoformat()
        }
        
        self._schedule[day.value].append(session)
        self._last_updated = datetime.now()
        return True
    
    def _has_conflict(self, 
                     day: str, 
                     start_time: time, 
                     end_time: time, 
                     teacher_id: Optional[str] = None,
                     exclude_session_id: Optional[str] = None) -> bool:
        """Check if there's a scheduling conflict.
        
        Args:
            day: Day of the week
            start_time: Proposed start time
            end_time: Proposed end time
            teacher_id: Optional teacher ID to check for conflicts
            exclude_session_id: Session ID to exclude from conflict check (for updates)
            
        Returns:
            bool: True if there's a conflict, False otherwise
        """
        for session in self._schedule.get(day, []):
            # Skip the session we're potentially updating
            if exclude_session_id and session.get('id') == exclude_session_id:
                continue
                
            # Check teacher availability
            if teacher_id and session.get('teacher_id') == teacher_id:
                # Check time overlap
                existing_start = datetime.strptime(session['start_time'], '%H:%M').time()
                existing_end = datetime.strptime(session['end_time'], '%H:%M').time()
                
                if (start_time < existing_end and end_time > existing_start):
                    return True
                    
        return False
    
    def update_class_session(self,
                           session_id: str,
                           new_day: Optional[Weekday] = None,
                           new_start_time: Optional[time] = None,
                           new_end_time: Optional[time] = None,
                           new_room: Optional[str] = None) -> bool:
        """Update an existing class session.
        
        Args:
            session_id: ID of the session to update
            new_day: New day of the week
            new_start_time: New start time
            new_end_time: New end time
            new_room: New room/location
            
        Returns:
            bool: True if updated successfully, False if not found or conflict
        """
        session = None
        day_found = None
        
        # Find the session
        for day, sessions in self._schedule.items():
            for s in sessions:
                if s['id'] == session_id:
                    session = s
                    day_found = day
                    break
            if session:
                break
                
        if not session:
            return False
            
        # Check for conflicts with the new time
        day = new_day.value if new_day else day_found
        start_time = new_start_time or datetime.strptime(session['start_time'], '%H:%M').time()
        end_time = new_end_time or datetime.strptime(session['end_time'], '%H:%M').time()
        
        if self._has_conflict(day, start_time, end_time, 
                            teacher_id=session['teacher_id'],
                            exclude_session_id=session_id):
            return False
        
        # Update the session
        if new_day and day_found != new_day.value:
            # Remove from old day and add to new day
            self._schedule[day_found] = [s for s in self._schedule[day_found] if s['id'] != session_id]
            self._schedule[new_day.value].append(session)
            
        if new_start_time:
            session['start_time'] = new_start_time.strftime('%H:%M')
        if new_end_time:
            session['end_time'] = new_end_time.strftime('%H:%M')
        if new_room is not None:
            session['room'] = new_room
            
        session['updated_at'] = datetime.now().isoformat()
        self._last_updated = datetime.now()
        return True
    
    def remove_class_session(self, session_id: str) -> bool:
        """Remove a class session from the schedule.
        
        Args:
            session_id: ID of the session to remove
            
        Returns:
            bool: True if removed, False if not found
        """
        for day in self._schedule:
            for i, session in enumerate(self._schedule[day]):
                if session['id'] == session_id:
                    self._schedule[day].pop(i)
                    self._last_updated = datetime.now()
                    return True
        return False
    
    def get_daily_schedule(self, day: Weekday) -> List[Dict]:
        """Get the schedule for a specific day."""
        return sorted(
            self._schedule.get(day.value, []),
            key=lambda x: x['start_time']
        )
    
    def get_teacher_schedule(self, teacher_id: str) -> Dict[str, List[Dict]]:
        """Get schedule for a specific teacher."""
        result = {day.value: [] for day in Weekday}
        
        for day, sessions in self._schedule.items():
            for session in sessions:
                if session['teacher_id'] == teacher_id:
                    result[day].append(session)
                    
        # Sort each day's sessions by start time
        for day in result:
            result[day].sort(key=lambda x: x['start_time'])
            
        return result
    
    def add_exception(self, 
                     date: datetime,
                     reason: str,
                     is_holiday: bool = False,
                     make_up_date: Optional[datetime] = None) -> str:
        """Add an exception to the schedule (e.g., holiday, special event).
        
        Args:
            date: Date of the exception
            reason: Reason for the exception
            is_holiday: Whether this is a holiday
            make_up_date: Optional make-up date if classes are rescheduled
            
        Returns:
            str: ID of the created exception
        """
        exception_id = f"exc_{len(str(hash(str(datetime.now()))))[-6:]}"
        
        self._exceptions.append({
            'id': exception_id,
            'date': date.date().isoformat(),
            'reason': reason,
            'is_holiday': is_holiday,
            'make_up_date': make_up_date.date().isoformat() if make_up_date else None,
            'created_at': datetime.now().isoformat()
        })
        
        self._last_updated = datetime.now()
        return exception_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the schedule to a dictionary."""
        return {
            'id': self._id,
            'class_id': self._class_id,
            'start_date': self._start_date.isoformat(),
            'end_date': self._end_date.isoformat(),
            'type': self._type,
            'last_updated': self._last_updated.isoformat(),
            'schedule': self._schedule,
            'exceptions': self._exceptions
        }
