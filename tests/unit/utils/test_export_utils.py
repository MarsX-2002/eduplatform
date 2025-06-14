"""Unit tests for export_utils.py"""
import os
import tempfile
import unittest
import pandas as pd
import sqlite3

from eduplatform.utils.export_utils import ExportUtils


class TestExportUtils(unittest.TestCase):
    """Test cases for ExportUtils class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data = [
            {"id": 1, "name": "John Doe", "email": "john@example.com", "score": 85.5},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "score": 92.0},
            {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "score": 78.5},
        ]
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests."""
        # Clean up any created files
        for root, _, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            os.rmdir(root)
    
    def test_export_to_xlsx(self):
        """Test exporting data to Excel format."""
        output_path = os.path.join(self.temp_dir, "test_export.xlsx")
        
        # Export data
        result_path = ExportUtils.export_data(
            data=self.test_data,
            output_path=output_path,
            format='xlsx'
        )
        
        # Verify file was created
        self.assertTrue(os.path.exists(result_path))
        
        # Verify content
        df = pd.read_excel(result_path)
        self.assertEqual(len(df), len(self.test_data))
        self.assertListEqual(list(df['name']), [item['name'] for item in self.test_data])
    
    def test_export_to_csv(self):
        """Test exporting data to CSV format."""
        output_path = os.path.join(self.temp_dir, "test_export.csv")
        
        # Export data
        result_path = ExportUtils.export_data(
            data=self.test_data,
            output_path=output_path,
            format='csv'
        )
        
        # Verify file was created
        self.assertTrue(os.path.exists(result_path))
        
        # Verify content
        df = pd.read_csv(result_path)
        self.assertEqual(len(df), len(self.test_data))
        self.assertListEqual(list(df['name']), [item['name'] for item in self.test_data])
    
    def test_export_to_sqlite(self):
        """Test exporting data to SQLite format."""
        output_path = os.path.join(self.temp_dir, "test_export.db")
        
        # Export data
        result_path = ExportUtils.export_data(
            data=self.test_data,
            output_path=output_path,
            format='sqlite',
            table_name='test_table'
        )
        
        # Verify file was created
        self.assertTrue(os.path.exists(result_path))
        
        # Verify content
        conn = sqlite3.connect(result_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        self.assertEqual(count, len(self.test_data))
        
        # Check if metadata table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='export_metadata'")
        self.assertIsNotNone(cursor.fetchone())
        
        conn.close()
    
    def test_export_with_invalid_format(self):
        """Test exporting with an invalid format raises an error."""
        with self.assertRaises(ValueError):
            ExportUtils.export_data(
                data=self.test_data,
                output_path=os.path.join(self.temp_dir, "test.txt"),
                format='invalid_format'
            )
    
    def test_export_empty_data(self):
        """Test exporting empty data raises an error."""
        with self.assertRaises(ValueError):
            ExportUtils.export_data(
                data=[],
                output_path=os.path.join(self.temp_dir, "empty.xlsx"),
                format='xlsx'
            )


if __name__ == '__main__':
    unittest.main()
