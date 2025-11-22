"""
PDF document parser using pdfminer.six - Good for text extraction
"""
from typing import Dict, List
from pathlib import Path
try:
    from pdfminer.high_level import extract_text, extract_pages
    from pdfminer.layout import LTTextContainer
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False


class PDFMinerParser:
    """Parse PDF documents using pdfminer.six"""
    
    def __init__(self):
        self.name = "pdfminer_parser"
    
    def parse(self, file_path: str) -> Dict:
        """
        Parse PDF file using pdfminer.six
        
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
        
        if not PDFMINER_AVAILABLE:
            result["error"] = "pdfminer.six library not available"
            return result
        
        try:
            # Extract full text
            full_text = extract_text(file_path)
            result["text"] = full_text
            
            # Extract pages with layout information
            pages = list(extract_pages(file_path))
            result["metadata"]["total_pages"] = len(pages)
            result["metadata"]["method"] = "pdfminer.six"
            
            full_text_pages = []
            for i, page_layout in enumerate(pages):
                page_text = ""
                text_elements = []
                
                # Extract text elements with position info
                for element in page_layout:
                    if isinstance(element, LTTextContainer):
                        element_text = element.get_text()
                        page_text += element_text + "\n"
                        text_elements.append({
                            "text": element_text.strip(),
                            "bbox": element.bbox  # (x0, y0, x1, y1)
                        })
                
                full_text_pages.append(page_text)
                
                page_data = {
                    "page_number": i + 1,
                    "text": page_text,
                    "text_elements_count": len(text_elements),
                    "layout_info": "available"
                }
                result["pages"].append(page_data)
            
            # Update full text with page-separated version
            result["text"] = "\n\n--- Page Break ---\n\n".join(full_text_pages)
            
            result["metadata"]["extraction_method"] = "layout_aware"
        
        except Exception as e:
            result["error"] = f"Failed to parse PDF with pdfminer: {str(e)}"
        
        return result

