"""
CLI commands for exporting data in various formats.
"""
import os
from typing import Optional

from ..services.export_service import ExportService
from ..utils.export_utils import ExportUtils

class ExportCommands:
    """CLI commands for data export functionality."""
    
    def __init__(self, export_service: ExportService):
        """Initialize with required services."""
        self.export_service = export_service
        
    def do_export_my_data(self, arg: str) -> None:
        """Export all data for the current user.
        
        Usage: export_my_data [format=xlsx] [output_dir=exports]
        
        Args:
            format: Export format (xlsx, csv, sqlite)
            output_dir: Directory to save exported files
        """
        if not hasattr(self, 'current_user') or not self.current_user:
            print("Error: You must be logged in to export your data.")
            return
            
        # Parse arguments
        args = self._parse_export_args(arg)
        format = args.get('format', 'xlsx')
        output_dir = args.get('output_dir', 'exports')
        
        try:
            print(f"Exporting your data to {format.upper()} format...")
            result = self.export_service.export_user_data(
                user_id=self.current_user._id,
                output_dir=output_dir,
                format=format
            )
            
            print("\nExport completed successfully!")
            print(f"Exported files:")
            for data_type, path in result.items():
                if data_type != 'manifest':
                    print(f"- {data_type}: {os.path.abspath(path)}")
            
            if 'manifest' in result:
                print(f"\nManifest file: {os.path.abspath(result['manifest'])}")
                
        except Exception as e:
            print(f"Error exporting data: {str(e)}")
    
    def do_export_class(self, arg: str) -> None:
        """Export data for a class (Teacher/Admin only).
        
        Usage: export_class <class_id> [format=xlsx] [output_dir=exports]
        
        Args:
            class_id: ID of the class to export
            format: Export format (xlsx, csv, sqlite)
            output_dir: Directory to save exported files
        """
        if not hasattr(self, 'current_user') or not self.current_user:
            print("Error: You must be logged in to export class data.")
            return
            
        # Check permissions - only teachers and admins can export class data
        from ..models.user import Teacher, Admin
        if not isinstance(self.current_user, (Teacher, Admin)):
            print("Error: Only teachers and administrators can export class data.")
            return
            
        # Parse arguments
        args = self._parse_export_args(arg)
        
        if not args.get('class_id'):
            print("Error: Class ID is required.")
            print("Usage: export_class <class_id> [format=xlsx] [output_dir=exports]")
            return
            
        class_id = args['class_id']
        format = args.get('format', 'xlsx')
        output_dir = args.get('output_dir', 'exports')
        
        try:
            print(f"Exporting data for class {class_id} to {format.upper()} format...")
            result = self.export_service.export_class_data(
                class_id=class_id,
                output_dir=output_dir,
                format=format
            )
            
            print("\nExport completed successfully!")
            print(f"Exported files:")
            for data_type, path in result.items():
                if data_type != 'manifest':
                    print(f"- {data_type}: {os.path.abspath(path)}")
            
            if 'manifest' in result:
                print(f"\nManifest file: {os.path.abspath(result['manifest'])}")
                
        except Exception as e:
            print(f"Error exporting class data: {str(e)}")
    
    def do_export_school(self, arg: str) -> None:
        """Export all school data (Admin only).
        
        Usage: export_school [format=xlsx] [output_dir=exports]
        
        Args:
            format: Export format (xlsx, csv, sqlite)
            output_dir: Directory to save exported files
        """
        if not hasattr(self, 'current_user') or not self.current_user:
            print("Error: You must be logged in to export school data.")
            return
            
        # Check permissions - only admins can export all school data
        from ..models.user import Admin
        if not isinstance(self.current_user, Admin):
            print("Error: Only administrators can export all school data.")
            return
            
        # Parse arguments
        args = self._parse_export_args(arg)
        format = args.get('format', 'xlsx')
        output_dir = args.get('output_dir', 'exports')
        
        try:
            confirm = input("WARNING: This will export all school data. Continue? (y/n): ")
            if confirm.lower() != 'y':
                print("Export cancelled.")
                return
                
            print(f"Exporting all school data to {format.upper()} format...")
            result = self.export_service.export_school_data(
                output_dir=output_dir,
                format=format
            )
            
            print("\nExport completed successfully!")
            print(f"Exported files:")
            for data_type, path in result.items():
                if data_type != 'manifest':
                    print(f"- {data_type}: {os.path.abspath(path)}")
            
            if 'manifest' in result:
                print(f"\nManifest file: {os.path.abspath(result['manifest'])}")
                
        except Exception as e:
            print(f"Error exporting school data: {str(e)}")
    
    def help_export_my_data(self) -> None:
        """Show help for the export_my_data command."""
        print("\nExport all your personal data.")
        print("Usage: export_my_data [format=xlsx] [output_dir=exports]")
        print("  format:     Output format (xlsx, csv, or sqlite)")
        print("  output_dir: Directory to save exported files (default: 'exports')")
        print("\nExample: export_my_data format=csv output_dir=my_data")
    
    def help_export_class(self) -> None:
        """Show help for the export_class command."""
        print("\nExport data for a specific class (Teacher/Admin only).")
        print("Usage: export_class <class_id> [format=xlsx] [output_dir=exports]")
        print("  class_id:   ID of the class to export")
        print("  format:     Output format (xlsx, csv, or sqlite)")
        print("  output_dir: Directory to save exported files (default: 'exports')")
        print("\nExample: export_class class_123 format=xlsx")
    
    def help_export_school(self) -> None:
        """Show help for the export_school command."""
        print("\nExport all school data (Admin only).")
        print("Usage: export_school [format=xlsx] [output_dir=exports]")
        print("  format:     Output format (xlsx, csv, or sqlite)")
        print("  output_dir: Directory to save exported files (default: 'exports')")
        print("\nExample: export_school format=sqlite output_dir=school_data")
    
    def _parse_export_args(self, arg: str) -> dict:
        """Parse export command arguments."""
        args = {}
        
        # Split the argument string into key=value pairs
        parts = arg.split()
        
        # First argument without a key is treated as class_id for export_class
        if parts and '=' not in parts[0]:
            args['class_id'] = parts[0]
            parts = parts[1:]
        
        # Parse key=value pairs
        for part in parts:
            if '=' in part:
                key, value = part.split('=', 1)
                args[key.lower()] = value.lower()
        
        # Set defaults if not provided
        if 'format' not in args:
            args['format'] = 'xlsx'
        if 'output_dir' not in args:
            args['output_dir'] = 'exports'
            
        return args
