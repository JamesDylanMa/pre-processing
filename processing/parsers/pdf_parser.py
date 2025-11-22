"""
PDF document parser
"""
from typing import Dict, List
from pathlib import Path
import PyPDF2
import pdfplumber


class PDFParser:
    """Parse PDF documents"""
    
    def __init__(self):
        self.name = "pdf_parser"
    
    def parse(self, file_path: str) -> Dict:
        """
        Parse PDF file and extract content
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with extracted content
        """
        result = {
            "file_path": file_path,
            "parser": self.name,
            "pages": [],
            "text": "",
            "metadata": {}
        }
        
        # Try pdfplumber first (better for tables and complex layouts)
        try:
            with pdfplumber.open(file_path) as pdf:
                result["metadata"]["total_pages"] = len(pdf.pages)
                result["metadata"]["method"] = "pdfplumber"
                
                full_text = []
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    full_text.append(page_text)
                    
                    # Extract tables if any
                    tables = page.extract_tables()
                    
                    page_data = {
                        "page_number": i + 1,
                        "text": page_text,
                        "tables": tables if tables else []
                    }
                    result["pages"].append(page_data)
                
                result["text"] = "\n\n".join(full_text)
        
        except Exception as e:
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    result["metadata"]["total_pages"] = len(pdf_reader.pages)
                    result["metadata"]["method"] = "PyPDF2"
                    
                    full_text = []
                    for i, page in enumerate(pdf_reader.pages):
                        page_text = page.extract_text() or ""
                        full_text.append(page_text)
                        
                        page_data = {
                            "page_number": i + 1,
                            "text": page_text,
                            "tables": []
                        }
                        result["pages"].append(page_data)
                    
                    result["text"] = "\n\n".join(full_text)
                    
                    # Extract metadata
                    if pdf_reader.metadata:
                        result["metadata"]["document_info"] = {
                            k: str(v) for k, v in pdf_reader.metadata.items()
                        }
            
            except Exception as e2:
                result["error"] = f"Failed to parse PDF: {str(e2)}"
        
        return result


