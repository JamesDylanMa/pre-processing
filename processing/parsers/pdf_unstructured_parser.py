"""
PDF document parser using unstructured library
unstructured is a free, open-source library for extracting structured data from documents
Supports various document types including PDFs, Word, HTML, etc.
"""
from typing import Dict, List
from pathlib import Path
try:
    from unstructured.partition.pdf import partition_pdf
    from unstructured.chunking.title import chunk_by_title
    UNSTRUCTURED_AVAILABLE = True
except ImportError:
    UNSTRUCTURED_AVAILABLE = False


class UnstructuredParser:
    """Parse PDF documents using unstructured library"""
    
    def __init__(self):
        self.name = "unstructured_parser"
    
    def parse(self, file_path: str) -> Dict:
        """
        Parse PDF file using unstructured library
        
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
        
        if not UNSTRUCTURED_AVAILABLE:
            result["error"] = "unstructured library not available. Install with: pip install unstructured[pdf]"
            return result
        
        try:
            # Partition PDF into elements
            elements = partition_pdf(
                filename=file_path,
                strategy="hi_res",  # High resolution strategy for better accuracy
                infer_table_structure=True,  # Extract tables
                extract_images_in_pdf=False,  # Skip images for faster processing
            )
            
            result["metadata"]["method"] = "unstructured"
            result["metadata"]["total_elements"] = len(elements)
            
            # Organize elements by type
            text_elements = []
            table_elements = []
            title_elements = []
            
            for element in elements:
                element_dict = {
                    "type": element.__class__.__name__,
                    "text": str(element),
                    "metadata": element.metadata.to_dict() if hasattr(element, 'metadata') else {}
                }
                
                result["elements"].append(element_dict)
                
                # Categorize elements
                if "Table" in element.__class__.__name__:
                    table_elements.append(element_dict)
                elif "Title" in element.__class__.__name__:
                    title_elements.append(element_dict)
                else:
                    text_elements.append(element_dict)
            
            # Extract text from all elements
            full_text = [str(elem) for elem in elements]
            result["text"] = "\n\n".join(full_text)
            
            # Extract tables
            tables = []
            for elem in elements:
                if "Table" in elem.__class__.__name__:
                    if hasattr(elem, 'metadata') and hasattr(elem.metadata, 'text_as_html'):
                        # Convert HTML table to structured data
                        table_data = {
                            "html": elem.metadata.text_as_html,
                            "text": str(elem)
                        }
                        tables.append(table_data)
            
            result["tables"] = tables
            result["metadata"]["text_elements"] = len(text_elements)
            result["metadata"]["table_elements"] = len(table_elements)
            result["metadata"]["title_elements"] = len(title_elements)
            
            # Create pages structure (group elements by page if available)
            pages_dict = {}
            for i, element in enumerate(elements):
                page_num = 1
                if hasattr(element, 'metadata') and hasattr(element.metadata, 'page_number'):
                    page_num = element.metadata.page_number
                elif hasattr(element, 'metadata') and 'page_number' in element.metadata.to_dict():
                    page_num = element.metadata.to_dict().get('page_number', 1)
                
                if page_num not in pages_dict:
                    pages_dict[page_num] = {
                        "page_number": page_num,
                        "text": "",
                        "elements": []
                    }
                
                pages_dict[page_num]["text"] += str(element) + "\n\n"
                pages_dict[page_num]["elements"].append({
                    "type": element.__class__.__name__,
                    "text": str(element)
                })
            
            # Convert to pages list
            for page_num in sorted(pages_dict.keys()):
                result["pages"].append(pages_dict[page_num])
            
            result["metadata"]["total_pages"] = len(pages_dict) if pages_dict else 1
        
        except Exception as e:
            result["error"] = f"Failed to parse PDF with unstructured: {str(e)}"
        
        return result

