#!/usr/bin/env python3
"""
EduPlatform CLI - Command Line Interface for the Educational Platform
"""
import os
import sys
import cmd
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Type, Union

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import repositories
from eduplatform.repositories.user_repository import UserRepository
from eduplatform.repositories.assignment_repository import AssignmentRepository
from eduplatform.repositories.grade_repository import GradeRepository
from eduplatform.repositories.notification_repository import NotificationRepository
from eduplatform.repositories.schedule_repository import ScheduleRepository

# Import models
from eduplatform.models.user import User, UserRole
from eduplatform.models.student import Student
from eduplatform.models.teacher import Teacher
from eduplatform.models.parent import Parent
from eduplatform.models.admin import Admin
from eduplatform.models.assignment import Assignment, AssignmentStatus, AssignmentDifficulty
from eduplatform.models.grade import Grade, GradeType
from eduplatform.models.notification import Notification, NotificationType, NotificationPriority
from eduplatform.models.schedule import Schedule, Weekday

# Import services
from eduplatform.services.auth_service import AuthService
from eduplatform.services.assignment_service import AssignmentService
from eduplatform.services.grade_service import GradeService
from eduplatform.services.export_service import ExportService

# Import export commands
from .export_commands import ExportCommands

class EduPlatformCLI(cmd.Cmd):
    """Command-line interface for the EduPlatform."""
    
    intro = """
    ===========================================
      Welcome to EduPlatform - CLI Interface
    ===========================================
    Type 'help' for a list of commands.
    Type 'exit' or 'quit' to exit the program.
    """
    
    prompt = 'eduplatform> '
    
    def __init__(self):
        """Initialize the CLI with repositories and services."""
        super().__init__()
        
        # Initialize repositories
        self.user_repo = UserRepository()
        self.assignment_repo = AssignmentRepository()
        self.grade_repo = GradeRepository()
        self.notification_repo = NotificationRepository()
        self.schedule_repo = ScheduleRepository()
        
        # Initialize services
        self.auth_service = AuthService(
            user_repository=self.user_repo,
            notification_repository=self.notification_repo,
            jwt_secret='your-secret-key-here',  # In production, use a secure secret key
            jwt_expire_hours=24
        )
        
        self.assignment_service = AssignmentService(
            assignment_repo=self.assignment_repo,
            grade_repo=self.grade_repo,
            user_repo=self.user_repo,
            notification_repo=self.notification_repo
        )
        
        self.grade_service = GradeService(
            grade_repo=self.grade_repo,
            user_repo=self.user_repo,
            notification_repo=self.notification_repo
        )
        
        # Initialize export service
        self.export_service = ExportService(
            auth_service=self.auth_service,
            assignment_service=self.assignment_service,
            grade_service=self.grade_service
        )
        
        # Initialize export commands
        self.export_commands = ExportCommands(self.export_service)
        
        # Current user session
        self.current_user = None
        self.current_user_type = None
        self.auth_token = None
    
    # ===== Export Commands =====
    
    def do_export_my_data(self, arg):
        """Export all your personal data."""
        if not hasattr(self.export_commands, 'current_user'):
            self.export_commands.current_user = self.current_user
        return self.export_commands.do_export_my_data(arg)
    
    def do_export_class(self, arg):
        """Export data for a class (Teacher/Admin only)."""
        if not hasattr(self.export_commands, 'current_user'):
            self.export_commands.current_user = self.current_user
        return self.export_commands.do_export_class(arg)
    
    def do_export_school(self, arg):
        """Export all school data (Admin only)."""
        if not hasattr(self.export_commands, 'current_user'):
            self.export_commands.current_user = self.current_user
        return self.export_commands.do_export_school(arg)
    
    # ===== Authentication Commands =====
    
    def do_register(self, arg):
        """Register a new user.
        Usage: register <role> "<full_name>" <email> <password> [phone] "[address]"
        
        Examples:
            register admin "John Doe" john@example.com mypassword
            register teacher "Jane Smith" jane@example.com mypassword 1234567890 "123 Main St"
        
        Roles: student, teacher, parent, admin
        """
        print("\n[CLI] Starting user registration process")
        
        try:
            import shlex
            args = shlex.split(arg)
            
            if len(args) < 4:
                print("Error: Missing required arguments. Usage: register <role> \"<full_name>\" <email> <password> [phone] [address]")
                print("Note: Enclose names and addresses with spaces in quotes")
                return
                
            role_map = {
                'student': Student,
                'teacher': Teacher,
                'parent': Parent,
                'admin': Admin
            }
            
            role = args[0].lower()
            print(f"[CLI] Registering user with role: {role}")
            
            if role not in role_map:
                print(f"Error: Invalid role. Must be one of: {', '.join(role_map.keys())}")
                return
                
            # Extract arguments with proper handling of optional fields
            full_name = args[1]
            email = args[2]
            password = args[3]
            
            # Handle optional phone and address
            phone = None
            address = None
            
            if len(args) > 4:
                # If there's a 5th argument, it's either a phone number or address
                if len(args) == 5:
                    # If it's just one more argument, treat it as phone if it's all digits
                    if args[4].isdigit():
                        phone = args[4]
                    else:
                        address = args[4]
                else:
                    # If there are 6+ arguments, 4th is phone, rest is address
                    phone = args[4]
                    address = ' '.join(args[5:])
            
            print(f"[CLI] Registration details - Name: {full_name}, Email: {email}")
            if phone:
                print(f"[CLI] Phone: {phone}")
            if address:
                print(f"[CLI] Address: {address}")
            
            # Create a dictionary of kwargs to pass to register_user
            user_kwargs = {
                'user_type': role_map[role],
                'full_name': full_name,
                'email': email,
                'password': password
            }
            
            # Add optional fields if provided
            if phone:
                user_kwargs['phone'] = phone
            if address:
                user_kwargs['address'] = address
            
            print("[CLI] Calling auth_service.register_user")
                
            # Call register_user with the prepared arguments
            result = self.auth_service.register_user(**user_kwargs)
            print(f"[CLI] auth_service.register_user returned: {type(result)}")
            
            if not result:
                print("Error: Registration failed - No result returned")
                return
                
            if not isinstance(result, dict):
                print(f"Error: Expected dict result, got {type(result).__name__}")
                return
                
            if 'user' not in result:
                print("Error: Registration failed - No user in result")
                print(f"Result keys: {result.keys() if hasattr(result, 'keys') else 'Not a dictionary'}")
                return
                
            print("[CLI] Registration successful, processing result...")
            
            self.current_user = result['user']
            self.current_user_type = result.get('user_type', 'user')
            self.auth_token = result.get('token')
            
            print(f"\n[CLI] Successfully registered and logged in as {self.current_user._full_name} ({self.current_user_type})")
            print(f"Welcome to EduPlatform!")
            
        except ValueError as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"\n[CLI] An unexpected error occurred during registration:")
            print(f"Type: {type(e).__name__}")
            print(f"Error: {str(e)}")
            print("\nPlease check the input and try again.")
    
    def do_login(self, arg):
        """Login to an existing account.
        Usage: login <email> <password>
        """
        if self.current_user:
            print(f"You are already logged in as {self.current_user._full_name}")
            return
            
        args = arg.split()
        if len(args) != 2:
            print("Error: Invalid arguments. Usage: login <email> <password>")
            return
            
        email, password = args
        
        result = self.auth_service.login(email, password)
        if not result:
            print("Error: Invalid email or password")
            return
            
        self.current_user = result['user']
        self.current_user_type = result['user_type']
        self.auth_token = result['token']
        
        print(f"\nSuccessfully logged in as {self.current_user._full_name} ({self.current_user_type})")
        self._show_unread_notifications()
    
    def do_logout(self, arg):
        """Logout of the current account."""
        if not self.current_user:
            print("You are not logged in.")
            return
            
        print(f"Goodbye, {self.current_user._full_name}!")
        self.current_user = None
        self.current_user_type = None
        self.auth_token = None
    
    def do_whoami(self, arg):
        """Show information about the currently logged-in user."""
        if not self.current_user:
            print("You are not logged in.")
            return
            
        print(f"\n=== User Information ===")
        print(f"Name: {self.current_user._full_name}")
        print(f"Email: {self.current_user._email}")
        print(f"Role: {self.current_user_type}")
        
        if hasattr(self.current_user, '_grade'):
            print(f"Grade: {self.current_user._grade}")
        if hasattr(self.current_user, '_subjects'):
            print(f"Subjects: {', '.join(self.current_user._subjects.keys())}")
        if hasattr(self.current_user, '_phone'):
            print(f"Phone: {self.current_user._phone}")
        if hasattr(self.current_user, '_address'):
            print(f"Address: {self.current_user._address}")
    
    # ===== Assignment Commands =====
    
    def do_create_assignment(self, arg):
        """Create a new assignment (Teacher only).
        Usage: create_assignment <title> <subject> <class_id> <due_date> [max_points=100] [difficulty=medium]
        """
        if not self._require_authentication() or not self._require_role('teacher'):
            return
            
        args = arg.split()
        if len(args) < 4:
            print("Error: Missing required arguments. Usage: create_assignment <title> <subject> <class_id> <due_date> [max_points=100] [difficulty=medium]")
            return
            
        try:
            title = args[0]
            subject = args[1]
            class_id = args[2]
            due_date = datetime.strptime(args[3], '%Y-%m-%d')
            max_points = float(args[4]) if len(args) > 4 else 100.0
            difficulty = args[5].lower() if len(args) > 5 else 'medium'
            
            # Get description from user
            print("Enter assignment description (press Enter on a blank line to finish):")
            description_lines = []
            while True:
                line = input("> ")
                if not line.strip():
                    break
                description_lines.append(line)
            description = '\n'.join(description_lines)
            
            assignment = self.assignment_service.create_assignment(
                teacher_id=self.current_user._id,
                title=title,
                description=description,
                subject=subject,
                class_id=class_id,
                due_date=due_date,
                max_points=max_points,
                difficulty=difficulty
            )
            
            print(f"\nAssignment created successfully!")
            print(f"ID: {assignment._id}")
            print(f"Title: {assignment._title}")
            print(f"Subject: {assignment._subject}")
            print(f"Due: {assignment._due_date.strftime('%Y-%m-%d')}")
            print(f"Max Points: {assignment._max_points}")
            print(f"Difficulty: {assignment._difficulty.value}")
            
        except ValueError as e:
            print(f"Error: {str(e)}")
    
    def do_list_assignments(self, arg):
        """List assignments.
        Usage: list_assignments [status] [subject]
        Status options: pending, submitted, graded, overdue (for students)
                        draft, published, graded (for teachers)
        """
        if not self._require_authentication():
            return
            
        args = arg.split()
        status = args[0] if args else None
        subject = args[1] if len(args) > 1 else None
        
        if self.current_user_type == 'student':
            assignments = self.assignment_service.get_student_assignments(
                student_id=self.current_user._id,
                status=status,
                subject=subject
            )
            
            if not assignments:
                print("No assignments found.")
                return
                
            print("\n=== Your Assignments ===")
            for i, a in enumerate(assignments, 1):
                print(f"\n{i}. {a['title']} ({a['subject']})")
                print(f"   Due: {a['due_date']} | Status: {a['status'].upper()}")
                print(f"   Max Points: {a['max_points']} | Difficulty: {a['difficulty'].title()}")
                if a['status'] == 'graded' and a['submission'] and 'grade' in a['submission']:
                    print(f"   Grade: {a['submission']['grade']}/{a['max_points']}")
        
        elif self.current_user_type == 'teacher':
            assignments = self.assignment_service.get_teacher_assignments(
                teacher_id=self.current_user._id,
                status=status,
                class_id=subject  # Reusing subject parameter as class_id for simplicity
            )
            
            if not assignments:
                print("No assignments found.")
                return
                
            print("\n=== Your Assignments ===")
            for i, a in enumerate(assignments, 1):
                print(f"\n{i}. {a['title']} ({a['subject']})")
                print(f"   Class: {a['class_id']} | Due: {a['due_date']}")
                print(f"   Submissions: {a['total_submissions']} | Graded: {a['graded_submissions']}")
                print(f"   Status: {a['status'].upper()}")
    
    def do_submit_assignment(self, arg):
        """Submit an assignment (Student only).
        Usage: submit_assignment <assignment_id>
        """
        if not self._require_authentication() or not self._require_role('student'):
            return
            
        args = arg.split()
        if not args:
            print("Error: Missing assignment ID. Usage: submit_assignment <assignment_id>")
            return
            
        assignment_id = args[0]
        
        try:
            # Get assignment details
            assignment = self.assignment_service.get_assignment_details(assignment_id, self.current_user._id)
            if not assignment:
                print("Error: Assignment not found or you don't have permission to view it.")
                return
                
            print(f"\n=== Submitting Assignment ===")
            print(f"Title: {assignment['title']}")
            print(f"Subject: {assignment['subject']}")
            print(f"Due: {assignment['due_date']}")
            print(f"Max Points: {assignment['max_points']}")
            print("\nEnter your submission (press Enter on a blank line to finish):")
            
            # Get submission content
            content_lines = []
            while True:
                line = input("> ")
                if not line.strip():
                    break
                content_lines.append(line)
            content = '\n'.join(content_lines)
            
            if not content:
                print("Error: Submission cannot be empty.")
                return
                
            # Submit the assignment
            result = self.assignment_service.submit_assignment(
                student_id=self.current_user._id,
                assignment_id=assignment_id,
                content=content
            )
            
            print(f"\nAssignment submitted successfully!")
            print(f"Submission ID: {result['submission_id']}")
            print(f"Submitted at: {result['submitted_at']}")
            if result['is_late']:
                print("Note: This submission is late.")
                
        except ValueError as e:
            print(f"Error: {str(e)}")
    
    # ===== Grade Commands =====
    
    def do_grade_assignment(self, arg):
        """Grade a student's assignment (Teacher only).
        Usage: grade_assignment <submission_id> <grade> [comments]
        """
        if not self._require_authentication() or not self._require_role('teacher'):
            return
            
        args = arg.split()
        if len(args) < 2:
            print("Error: Missing required arguments. Usage: grade_assignment <submission_id> <grade> [comments]")
            return
            
        submission_id = args[0]
        try:
            grade = float(args[1])
        except ValueError:
            print("Error: Grade must be a number.")
            return
            
        comments = ' '.join(args[2:]) if len(args) > 2 else ''
        
        try:
            result = self.assignment_service.grade_assignment(
                teacher_id=self.current_user._id,
                submission_id=submission_id,
                grade=grade,
                feedback=comments
            )
            
            print(f"\nAssignment graded successfully!")
            print(f"Student: {result['student_id']}")
            print(f"Grade: {result['grade']}/{result['max_grade']}")
            if comments:
                print(f"Comments: {comments}")
                
        except ValueError as e:
            print(f"Error: {str(e)}")
    
    def do_view_grades(self, arg):
        """View grades for assignments.
        Usage: view_grades [subject] [type]
        Subject: Filter by subject (optional)
        Type: Filter by grade type (e.g., 'assignment', 'exam') (optional)
        """
        if not self._require_authentication():
            return
            
        args = arg.split()
        subject = args[0] if args else None
        grade_type = args[1] if len(args) > 1 else None
        
        try:
            if self.current_user_type == 'student':
                grades = self.grade_service.get_student_grades(
                    student_id=self.current_user._id,
                    subject=subject,
                    grade_type=grade_type
                )
                
                if not grades:
                    print("No grades found.")
                    return
                    
                print("\n=== Your Grades ===")
                for grade in grades:
                    print(f"\n{grade['subject']} - {grade['type'].title()}")
                    print(f"Score: {grade['score']}/{grade['max_score']} ({grade['percentage']:.1f}%) - {grade['letter_grade']}")
                    print(f"Teacher: {grade['teacher_name']}")
                    print(f"Date: {grade['created_at']}")
                    if grade['comments']:
                        print(f"Comments: {grade['comments']}")
            
            elif self.current_user_type == 'teacher':
                # For teachers, show grades for their classes
                print("Feature not implemented yet. Will show class gradebook.")
            
            elif self.current_user_type == 'parent':
                # For parents, show grades for their children
                if not hasattr(self.current_user, '_children') or not self.current_user._children:
                    print("No children linked to your account.")
                    return
                    
                print("\n=== Children's Grades ===")
                for child_id in self.current_user._children:
                    child = self.user_repo.get(child_id)
                    if not child:
                        continue
                        
                    print(f"\n{child._full_name}:")
                    grades = self.grade_service.get_student_grades(
                        student_id=child_id,
                        subject=subject,
                        grade_type=grade_type
                    )
                    
                    if not grades:
                        print("  No grades found.")
                        continue
                        
                    for grade in grades[:3]:  # Show top 3 most recent grades
                        print(f"  {grade['subject']}: {grade['score']}/{grade['max_score']} ({grade['percentage']:.1f}%) - {grade['letter_grade']}")
                    
                    if len(grades) > 3:
                        print(f"  ... and {len(grades) - 3} more grades")
            
            else:
                print("This feature is not available for your role.")
                
        except Exception as e:
            print(f"Error: {str(e)}")
    
    # ===== Notification Commands =====
    
    def do_notifications(self, arg):
        """View and manage notifications.
        Usage: notifications [read|unread|all] [mark_read <id>|clear]
        """
        if not self._require_authentication():
            return
            
        args = arg.split()
        show_read = True
        
        if args and args[0] == 'unread':
            show_read = False
            args = args[1:]
        elif args and args[0] == 'all':
            show_read = True
            args = args[1:]
        
        if args and args[0] == 'mark_read':
            if len(args) < 2:
                print("Error: Missing notification ID. Usage: notifications mark_read <id>")
                return
                
            notification_id = args[1]
            if self.notification_repo.mark_as_read(notification_id):
                print(f"Marked notification {notification_id} as read.")
            else:
                print(f"Error: Could not find notification with ID {notification_id}")
            return
            
        if args and args[0] == 'clear':
            count = self.notification_repo.mark_all_as_read(self.current_user._id)
            print(f"Marked {count} notifications as read.")
            return
            
        # Show notifications
        notifications = self.notification_repo.get_user_notifications(
            user_id=self.current_user._id,
            unread_only=not show_read
        )
        
        if not notifications:
            print("No notifications found." if show_read else "No unread notifications.")
            return
            
        print("\n=== Notifications ===")
        for i, notification in enumerate(notifications, 1):
            status = "[READ] " if notification._is_read else "[UNREAD] "
            print(f"\n{i}. {status}{notification._title}")
            print(f"   {notification._message}")
            print(f"   {notification._created_at.strftime('%Y-%m-%d %H:%M')}")
    
    # ===== Helper Methods =====
    
    def _require_authentication(self) -> bool:
        """Check if user is authenticated."""
        if not self.current_user:
            print("Error: You must be logged in to perform this action.")
            return False
        return True
    
    def _require_role(self, *roles: str) -> bool:
        """Check if current user has one of the required roles."""
        if not self.current_user or self.current_user_type.lower() not in roles:
            print(f"Error: This action requires {' or '.join(roles)} privileges.")
            return False
        return True
    
    def _show_unread_notifications(self) -> None:
        """Show a summary of unread notifications."""
        if not self.current_user:
            return
            
        unread_count = self.notification_repo.get_unread_count(self.current_user._id)
        if unread_count > 0:
            print(f"\nYou have {unread_count} unread notification{'s' if unread_count > 1 else ''}.")
            print("Type 'notifications' to view them.")
    
    # ===== System Commands =====
    
    def do_clear(self, arg):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def do_exit(self, arg):
        """Exit the application."""
        print("\nThank you for using EduPlatform. Goodbye!")
        return True
    
    def do_quit(self, arg):
        """Exit the application."""
        return self.do_exit(arg)
    
    def do_EOF(self, arg):
        """Handle Ctrl+D to exit."""
        print()  # Print a newline before exiting
        return self.do_exit(arg)


def main():
    """Main entry point for the EduPlatform CLI."""
    try:
        EduPlatformCLI().cmdloop()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
