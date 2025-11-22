"""
PDF document parser using PyMuPDF (fitz) - Fast and accurate
"""
from typing import Dict, List
from pathlib import Path
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class PyMuPDFParser:
    """Parse PDF documents using PyMuPDF (fitz)"""
    
    def __init__(self):
        self.name = "pymupdf_parser"
    
    def parse(self, file_path: str) -> Dict:
        """
        Parse PDF file using PyMuPDF
        
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
        
        if not PYMUPDF_AVAILABLE:
            result["error"] = "PyMuPDF library not available. Install with: pip install PyMuPDF"
            return result
        
        try:
            doc = fitz.open(file_path)
            
            result["metadata"]["total_pages"] = len(doc)
            result["metadata"]["method"] = "PyMuPDF"
            
            # Extract document metadata
            if doc.metadata:
                result["metadata"]["document_info"] = {
                    k: str(v) for k, v in doc.metadata.items()
                }
            
            full_text = []
            for i, page in enumerate(doc):
                # Extract text
                page_text = page.get_text()
                full_text.append(page_text)
                
                # Extract images info
                image_list = page.get_images()
                
                # Extract annotations
                annotations = []
                for annot in page.annots():
                    annotations.append({
                        "type": annot.type[1],
                        "content": annot.info.get("content", "")
                    })
                
                page_data = {
                    "page_number": i + 1,
                    "text": page_text,
                    "images_count": len(image_list),
                    "annotations": annotations
                }
                result["pages"].append(page_data)
            
            result["text"] = "\n\n".join(full_text)
            
            # Extract text blocks with formatting info
            blocks = []
            for page in doc:
                blocks.extend(page.get_text("blocks"))
            
            result["metadata"]["text_blocks_count"] = len(blocks)
            
            doc.close()
        
        except Exception as e:
            result["error"] = f"Failed to parse PDF with PyMuPDF: {str(e)}"
        
        return result

