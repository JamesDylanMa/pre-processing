"""
Excel document parser
"""
from typing import Dict, List
from pathlib import Path
import pandas as pd


class ExcelParser:
    """Parse Excel documents"""
    
    def __init__(self):
        self.name = "excel_parser"
    
    def parse(self, file_path: str) -> Dict:
        """
        Parse Excel file and extract content
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Dictionary with extracted content
        """
        result = {
            "file_path": file_path,
            "parser": self.name,
            "sheets": [],
            "metadata": {}
        }
        
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)
            result["metadata"]["sheet_names"] = excel_file.sheet_names
            result["metadata"]["total_sheets"] = len(excel_file.sheet_names)
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                sheet_data = {
                    "sheet_name": sheet_name,
                    "rows": df.shape[0],
                    "columns": df.shape[1],
                    "column_names": df.columns.tolist(),
                    "data": df.fillna("").to_dict('records'),  # Convert to list of dicts
                    "summary": {
                        "numeric_columns": df.select_dtypes(include=['number']).columns.tolist(),
                        "text_columns": df.select_dtypes(include=['object']).columns.tolist()
                    }
                }
                
                result["sheets"].append(sheet_data)
        
        except Exception as e:
            result["error"] = f"Failed to parse Excel file: {str(e)}"
        
        return result


