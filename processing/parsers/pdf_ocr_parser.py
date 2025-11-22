"""
PDF document parser using OCR (Tesseract) for scanned PDFs
"""
from typing import Dict, List
from pathlib import Path
try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class OCRParser:
    """Parse PDF documents using OCR (for scanned PDFs)"""
    
    def __init__(self):
        self.name = "ocr_parser"
    
    def parse(self, file_path: str) -> Dict:
        """
        Parse PDF file using OCR
        
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
        
        if not OCR_AVAILABLE:
            result["error"] = "OCR libraries not available. Install with: pip install pdf2image pytesseract"
            return result
        
        try:
            # Convert PDF to images
            images = convert_from_path(file_path)
            
            result["metadata"]["total_pages"] = len(images)
            result["metadata"]["method"] = "OCR (Tesseract)"
            
            full_text = []
            for i, image in enumerate(images):
                # Extract text using OCR
                page_text = pytesseract.image_to_string(image, lang='kor+eng')
                full_text.append(page_text)
                
                page_data = {
                    "page_number": i + 1,
                    "text": page_text,
                    "tables": [],
                    "ocr_confidence": "available"
                }
                result["pages"].append(page_data)
            
            result["text"] = "\n\n".join(full_text)
            result["metadata"]["is_scanned"] = True
            result["metadata"]["ocr_used"] = True
        
        except Exception as e:
            error_msg = str(e)
            # Check for common OCR errors
            if "tesseract" in error_msg.lower() or "not found" in error_msg.lower():
                result["error"] = "Tesseract OCR not found. Please install Tesseract OCR engine."
            elif "poppler" in error_msg.lower() or "pdf2image" in error_msg.lower():
                result["error"] = "Poppler not found. Please install Poppler for pdf2image."
            else:
                result["error"] = f"Failed to parse PDF with OCR: {error_msg}"
        
        return result

