from typing import Dict, List, Optional, Any, Union, Type
from .user import User, UserRole
from .student import Student
from .teacher import Teacher
from .parent import Parent
from datetime import datetime
import json

class Admin(User):
    """Admin class representing an administrator in the educational platform."""
    
    def __init__(self, full_name: str, email: str, password: str):
        """Initialize a new admin user.
        
        Args:
            full_name: Admin's full name
            email: Admin's email (must be unique)
            password: Admin's password (will be hashed)
        """
        super().__init__(full_name, email, password, UserRole.ADMIN)
        self._permissions = [
            'manage_users',
            'view_system_reports',
            'configure_system_settings',
            'manage_courses',
            'manage_classes',
            'audit_logs'
        ]
    
    def create_user(self, 
                  user_type: Type[Union[Student, Teacher, Parent, 'Admin']],
                  full_name: str, 
                  email: str, 
                  password: str,
                  **kwargs) -> Optional[Union[Student, Teacher, Parent, 'Admin']]:
        """Create a new user account.
        
        Args:
            user_type: The type of user to create (Student, Teacher, Parent, or Admin)
            full_name: User's full name
            email: User's email (must be unique)
            password: User's password
            **kwargs: Additional arguments specific to the user type
                      (e.g., grade for Student, subjects for Teacher)
                      
        Returns:
            The created user object if successful, None otherwise
        """
        try:
            if user_type == Student:
                if 'grade' not in kwargs:
                    raise ValueError("Grade is required for Student")
                return Student(full_name, email, password, kwargs['grade'])
                
            elif user_type == Teacher:
                return Teacher(full_name, email, password)
                
            elif user_type == Parent:
                return Parent(full_name, email, password)
                
            elif user_type == Admin:
                return Admin(full_name, email, password)
                
            else:
                raise ValueError(f"Invalid user type: {user_type.__name__}")
                
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def remove_user(self, user_id: str, users_list: list) -> bool:
        """Remove a user from the system.
        
        Args:
            user_id: ID of the user to remove
            users_list: List of user objects to search in
            
        Returns:
            bool: True if user was found and removed, False otherwise
        """
        for i, user in enumerate(users_list):
            if user._id == user_id:
                users_list.pop(i)
                return True
        return False
    
    def generate_report(self, 
                       report_type: str, 
                       data: list,
                       **filters) -> Dict[str, Any]:
        """Generate a system report.
        
        Args:
            report_type: Type of report to generate
            data: Data to generate the report from
            **filters: Filters to apply to the data
            
        Returns:
            Dict containing the report data
        """
        report = {
            'report_id': f"report_{len(str(hash(str(datetime.now()))))}",
            'type': report_type,
            'generated_at': datetime.now().isoformat(),
            'filters': filters,
            'data': []
        }
        
        if report_type == 'user_list':
            for user in data:
                user_data = user.get_profile()
                # Include only non-sensitive data in the report
                report['data'].append({
                    'id': user_data.get('id'),
                    'full_name': user_data.get('full_name'),
                    'email': user_data.get('email'),
                    'role': user_data.get('role'),
                    'created_at': user_data.get('created_at')
                })
                
        elif report_type == 'system_stats':
            # This would be more comprehensive in a real implementation
            user_counts = {'admin': 0, 'teacher': 0, 'student': 0, 'parent': 0}
            for user in data:
                if hasattr(user, '_role'):
                    role = user._role.value
                    if role in user_counts:
                        user_counts[role] += 1
            
            report['data'] = {
                'total_users': len(data),
                'user_counts': user_counts,
                'report_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        return report
    
    def export_to_xlsx(self, data: list, filename: str = 'export.xlsx') -> bool:
        """Export data to an Excel file.
        
        Args:
            data: List of objects to export
            filename: Name of the output file
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            # In a real implementation, we would use a library like openpyxl or pandas
            # This is a simplified version that just demonstrates the interface
            print(f"[DEBUG] Exporting {len(data)} records to {filename}")
            # Actual export logic would go here
            return True
        except Exception as e:
            print(f"Error exporting to XLSX: {e}")
            return False
    
    def export_to_csv(self, data: list, filename: str = 'export.csv') -> bool:
        """Export data to a CSV file.
        
        Args:
            data: List of objects to export
            filename: Name of the output file
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            # In a real implementation, we would use the csv module or pandas
            print(f"[DEBUG] Exporting {len(data)} records to {filename}")
            # Actual export logic would go here
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def export_to_sql(self, data: list, table_name: str) -> str:
        """Generate SQL INSERT statements for the data.
        
        Args:
            data: List of objects to export
            table_name: Name of the target database table
            
        Returns:
            str: SQL INSERT statements as a string
        """
        if not data:
            return "-- No data to export"
            
        # Get column names from the first item's profile
        sample = data[0].get_profile()
        columns = ', '.join(f'"{k}"' for k in sample.keys())
        
        # Generate INSERT statements
        inserts = []
        for item in data:
            profile = item.get_profile()
            values = ', '.join(
                f"'{str(v).replace("'", "''")}'" if v is not None else 'NULL' 
                for v in profile.values()
            )
            inserts.append(f"INSERT INTO {table_name} ({columns}) VALUES ({values});")
        
        return '\n'.join(inserts)
    
    def get_profile(self) -> Dict[str, Any]:
        """Get the admin's profile with additional admin-specific information."""
        base_profile = super().get_profile()
        base_profile.update({
            'permissions': self._permissions,
            'can_manage_users': 'manage_users' in self._permissions,
            'can_view_reports': 'view_system_reports' in self._permissions,
            'can_configure_system': 'configure_system_settings' in self._permissions
        })
        return base_profile
