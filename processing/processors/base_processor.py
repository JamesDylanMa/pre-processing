"""
Base processor class
"""
from abc import ABC, abstractmethod
from typing import Dict, List
from pathlib import Path

from processing.parsers.pdf_parser import PDFParser
from processing.parsers.word_parser import WordParser
from processing.parsers.excel_parser import ExcelParser
from processing.parsers.ppt_parser import PPTParser


class BaseProcessor(ABC):
    """Base class for all processors"""
    
    def __init__(self, name: str):
        self.name = name
        self.parsers = {
            'pdf': PDFParser(),
            'word': WordParser(),
            'excel': ExcelParser(),
            'powerpoint': PPTParser()
        }
    
    def get_parser(self, file_type: str):
        """Get appropriate parser for file type"""
        return self.parsers.get(file_type)
    
    @abstractmethod
    def process(self, file_path: str, file_type: str, **kwargs) -> Dict:
        """
        Process a file
        
        Args:
            file_path: Path to file
            file_type: Type of file
            **kwargs: Additional processing options
            
        Returns:
            Processed result dictionary
        """
        pass
    
    def parse_document(self, file_path: str, file_type: str) -> Dict:
        """Parse document using appropriate parser"""
        parser = self.get_parser(file_type)
        if parser:
            return parser.parse(file_path)
        else:
            return {
                "error": f"No parser available for file type: {file_type}",
                "file_path": file_path,
                "file_type": file_type
            }


