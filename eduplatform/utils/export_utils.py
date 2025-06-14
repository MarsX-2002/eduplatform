"""
Utility functions for exporting data to various formats.
"""
import os
import csv
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Type, TypeVar
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

# Type variable for generic type hints
T = TypeVar('T')

class ExportUtils:
    """Utility class for exporting data to various formats."""
    
    @staticmethod
    def to_xlsx(data: List[Dict[str, Any]], 
               output_path: str, 
               sheet_name: str = 'Data',
               include_index: bool = False) -> str:
        """Export data to an Excel (XLSX) file.
        
        Args:
            data: List of dictionaries containing the data to export
            output_path: Path to save the Excel file
            sheet_name: Name of the worksheet
            include_index: Whether to include an index column
            
        Returns:
            str: Path to the saved file
            
        Raises:
            ValueError: If data is empty or invalid
            IOError: If file cannot be written
        """
        if not data:
            raise ValueError("No data to export")
            
        try:
            # Ensure the output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                
            # Create a DataFrame and save to Excel
            df = pd.DataFrame(data)
            
            # Create a Pandas Excel writer using openpyxl as the engine
            with pd.ExcelWriter(
                output_path, 
                engine='openpyxl',
                mode='w',
                datetime_format='YYYY-MM-DD HH:MM:SS',
                date_format='YYYY-MM-DD'
            ) as writer:
                df.to_excel(
                    writer, 
                    sheet_name=sheet_name[:31],  # Excel sheet name max 31 chars
                    index=include_index,
                    freeze_panes=(1, 0)  # Freeze header row
                )
                
                # Get the workbook and worksheet objects
                workbook = writer.book
                worksheet = writer.sheets[sheet_name[:31]]
                
                # Format header
                header_font = Font(bold=True)
                for cell in worksheet[1]:
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal='center')
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    # Find the maximum length of content in the column
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    # Set column width with a little extra space
                    adjusted_width = (max_length + 2) * 1.1
                    worksheet.column_dimensions[column_letter].width = min(adjusted_width, 50)  # Max width 50
            
            return output_path
            
        except Exception as e:
            raise IOError(f"Failed to export to Excel: {str(e)}")
    
    @staticmethod
    def to_csv(data: List[Dict[str, Any]], 
              output_path: str,
              delimiter: str = ',',
              encoding: str = 'utf-8') -> str:
        """Export data to a CSV file.
        
        Args:
            data: List of dictionaries containing the data to export
            output_path: Path to save the CSV file
            delimiter: Field delimiter
            encoding: File encoding
            
        Returns:
            str: Path to the saved file
            
        Raises:
            ValueError: If data is empty or invalid
            IOError: If file cannot be written
        """
        if not data:
            raise ValueError("No data to export")
            
        try:
            # Ensure the output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                
            # Get all unique fieldnames from the data
            fieldnames = set()
            for item in data:
                fieldnames.update(item.keys())
            fieldnames = sorted(fieldnames)
            
            # Write data to CSV
            with open(output_path, 'w', newline='', encoding=encoding) as csvfile:
                writer = csv.DictWriter(
                    csvfile, 
                    fieldnames=fieldnames,
                    delimiter=delimiter,
                    quoting=csv.QUOTE_MINIMAL
                )
                writer.writeheader()
                writer.writerows(data)
                
            return output_path
            
        except Exception as e:
            raise IOError(f"Failed to export to CSV: {str(e)}")
    
    @classmethod
    def to_sqlite(cls, 
                 data: List[Dict[str, Any]], 
                 output_path: str,
                 table_name: str = 'exported_data',
                 if_exists: str = 'replace') -> str:
        """Export data to an SQLite database.
        
        Args:
            data: List of dictionaries containing the data to export
            output_path: Path to save the SQLite database
            table_name: Name of the table to create/update
            if_exists: What to do if table exists: 'fail', 'replace', or 'append'
            
        Returns:
            str: Path to the saved database file
            
        Raises:
            ValueError: If data is empty or invalid
            IOError: If file cannot be written
        """
        if not data:
            raise ValueError("No data to export")
            
        if if_exists not in ('fail', 'replace', 'append'):
            raise ValueError("if_exists must be one of: 'fail', 'replace', 'append'")
            
        try:
            # Ensure the output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Create a connection to the SQLite database
            conn = sqlite3.connect(output_path)
            
            # Create a DataFrame and save to SQLite
            df = pd.DataFrame(data)
            
            # Convert datetime columns to strings for SQLite compatibility
            for col in df.select_dtypes(include=['datetime64']).columns:
                df[col] = df[col].astype(str)
            
            # Export to SQLite
            df.to_sql(
                name=table_name,
                con=conn,
                if_exists=if_exists,
                index=False
            )
            
            # Add metadata table
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS export_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    export_timestamp TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    row_count INTEGER NOT NULL,
                    columns TEXT NOT NULL
                )
            ''')
            
            # Record export metadata
            cursor.execute('''
                INSERT INTO export_metadata 
                (export_timestamp, table_name, row_count, columns)
                VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                table_name,
                len(df),
                ','.join(df.columns)
            ))
            
            # Commit changes and close connection
            conn.commit()
            conn.close()
            
            return output_path
            
        except Exception as e:
            if 'conn' in locals():
                conn.close()
            raise IOError(f"Failed to export to SQLite: {str(e)}")
    
    @classmethod
    def export_data(cls, 
                   data: List[Dict[str, Any]], 
                   output_path: str,
                   format: str = 'xlsx',
                   **kwargs) -> str:
        """Export data to the specified format.
        
        Args:
            data: List of dictionaries containing the data to export
            output_path: Path to save the exported file
            format: Export format ('xlsx', 'csv', or 'sqlite')
            **kwargs: Additional arguments passed to the specific export method
            
        Returns:
            str: Path to the saved file
            
        Raises:
            ValueError: If format is not supported
        """
        format = format.lower()
        
        # Ensure the output file has the correct extension
        if not output_path.lower().endswith(f'.{format}'):
            output_path = f"{os.path.splitext(output_path)[0]}.{format}"
        
        if format == 'xlsx':
            return cls.to_xlsx(data, output_path, **kwargs)
        elif format == 'csv':
            return cls.to_csv(data, output_path, **kwargs)
        elif format == 'sqlite':
            return cls.to_sqlite(data, output_path, **kwargs)
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Example usage
if __name__ == "__main__":
    # Sample data
    sample_data = [
        {"id": 1, "name": "John Doe", "email": "john@example.com", "score": 85.5},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "score": 92.0},
        {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "score": 78.5},
    ]
    
    # Export to different formats
    try:
        # Export to Excel
        xlsx_path = ExportUtils.export_data(sample_data, "output/sample_data.xlsx")
        print(f"Exported to Excel: {xlsx_path}")
        
        # Export to CSV
        csv_path = ExportUtils.export_data(sample_data, "output/sample_data.csv")
        print(f"Exported to CSV: {csv_path}")
        
        # Export to SQLite
        db_path = ExportUtils.export_data(sample_data, "output/sample_data.db", format='sqlite')
        print(f"Exported to SQLite: {db_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
