"""
PDF document parser using pypdf (successor to PyPDF2) - Modern and actively maintained
"""
from typing import Dict, List
from pathlib import Path
try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    try:
        # Fallback to PyPDF2
        from PyPDF2 import PdfReader
        PYPDF_AVAILABLE = True
    except ImportError:
        PYPDF_AVAILABLE = False


class PyPDFParser:
    """Parse PDF documents using pypdf (modern PyPDF2 successor)"""
    
    def __init__(self):
        self.name = "pypdf_parser"
    
    def parse(self, file_path: str) -> Dict:
        """
        Parse PDF file using pypdf
        
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
        
        if not PYPDF_AVAILABLE:
            result["error"] = "pypdf or PyPDF2 library not available"
            return result
        
        try:
            pdf_reader = PdfReader(file_path)
            
            result["metadata"]["total_pages"] = len(pdf_reader.pages)
            result["metadata"]["method"] = "pypdf"
            
            # Extract document metadata
            if pdf_reader.metadata:
                result["metadata"]["document_info"] = {
                    k: str(v) for k, v in pdf_reader.metadata.items()
                }
            
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
            
            # Extract form fields if any
            if pdf_reader.metadata:
                result["metadata"]["has_forms"] = len(pdf_reader.pages) > 0
            
        except Exception as e:
            result["error"] = f"Failed to parse PDF with pypdf: {str(e)}"
        
        return result

