"""
PDF document parser using pdfquery
pdfquery is a free library for extracting data from PDFs using CSS-like selectors
Good for structured PDFs with consistent layouts
"""
from typing import Dict, List
from pathlib import Path
try:
    import pdfquery
    PDFQUERY_AVAILABLE = True
except ImportError:
    PDFQUERY_AVAILABLE = False


class PDFQueryParser:
    """Parse PDF documents using pdfquery"""
    
    def __init__(self):
        self.name = "pdfquery_parser"
    
    def parse(self, file_path: str) -> Dict:
        """
        Parse PDF file using pdfquery
        
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
            "elements": [],
            "metadata": {}
        }
        
        if not PDFQUERY_AVAILABLE:
            result["error"] = "pdfquery library not available. Install with: pip install pdfquery"
            return result
        
        try:
            # Load PDF
            pdf = pdfquery.PDFQuery(file_path)
            pdf.load()
            
            result["metadata"]["method"] = "pdfquery"
            result["metadata"]["total_pages"] = len(pdf.pq('LTPage'))
            
            # Extract all text elements
            text_elements = pdf.pq('LTTextLineHorizontal')
            
            # Group text by pages
            pages_dict = {}
            full_text = []
            
            for text_elem in text_elements:
                # Get page number
                page_elem = text_elem.getparent()
                while page_elem is not None and page_elem.tag != 'LTPage':
                    page_elem = page_elem.getparent()
                
                page_num = 1
                if page_elem is not None:
                    # Find page number
                    all_pages = pdf.pq('LTPage')
                    for idx, page in enumerate(all_pages):
                        if page == page_elem:
                            page_num = idx + 1
                            break
                
                # Extract text
                text_content = text_elem.text.strip()
                if text_content:
                    if page_num not in pages_dict:
                        pages_dict[page_num] = {
                            "page_number": page_num,
                            "text": "",
                            "elements": []
                        }
                    
                    pages_dict[page_num]["text"] += text_content + "\n"
                    pages_dict[page_num]["elements"].append({
                        "text": text_content,
                        "bbox": {
                            "x0": float(text_elem.get('x0', 0)),
                            "y0": float(text_elem.get('y0', 0)),
                            "x1": float(text_elem.get('x1', 0)),
                            "y1": float(text_elem.get('y1', 0))
                        }
                    })
                    full_text.append(text_content)
            
            result["text"] = "\n".join(full_text)
            result["metadata"]["total_elements"] = len(text_elements)
            
            # Convert to pages list
            for page_num in sorted(pages_dict.keys()):
                result["pages"].append(pages_dict[page_num])
            
            # Extract metadata
            result["metadata"]["has_text"] = len(full_text) > 0
            result["metadata"]["extraction_method"] = "CSS-like selectors"
        
        except Exception as e:
            result["error"] = f"Failed to parse PDF with pdfquery: {str(e)}"
        
        return result

