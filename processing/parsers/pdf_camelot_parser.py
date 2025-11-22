"""
PDF document parser using Camelot - Specialized for table extraction
"""
from typing import Dict, List
from pathlib import Path
try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False


class CamelotParser:
    """Parse PDF documents using Camelot (table extraction focused)"""
    
    def __init__(self):
        self.name = "camelot_parser"
    
    def parse(self, file_path: str) -> Dict:
        """
        Parse PDF file using Camelot (focus on tables)
        
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
            "tables": [],
            "metadata": {}
        }
        
        if not CAMELOT_AVAILABLE:
            result["error"] = "camelot-py library not available. Install with: pip install camelot-py[cv]"
            return result
        
        try:
            # Extract tables from all pages
            tables = camelot.read_pdf(file_path, pages='all', flavor='lattice')
            
            result["metadata"]["total_pages"] = len(set([t.page for t in tables]))
            result["metadata"]["method"] = "camelot"
            result["metadata"]["total_tables"] = len(tables)
            
            # Process tables
            all_text = []
            page_tables = {}
            
            for table in tables:
                page_num = table.page
                
                if page_num not in page_tables:
                    page_tables[page_num] = {
                        "page_number": page_num,
                        "tables": [],
                        "text": ""
                    }
                
                # Convert table to list of lists
                table_data = table.df.values.tolist()
                table_text = "\n".join([" | ".join([str(cell) for cell in row]) for row in table_data])
                
                page_tables[page_num]["tables"].append({
                    "data": table_data,
                    "accuracy": table.accuracy,
                    "whitespace": table.whitespace
                })
                
                page_tables[page_num]["text"] += table_text + "\n\n"
                all_text.append(table_text)
            
            # Convert to pages list
            for page_num in sorted(page_tables.keys()):
                result["pages"].append(page_tables[page_num])
            
            result["text"] = "\n\n--- Table ---\n\n".join(all_text)
            result["tables"] = [{"data": t.df.values.tolist(), "page": t.page} for t in tables]
            
        except Exception as e:
            error_msg = str(e)
            # Check for common Camelot errors
            if "java" in error_msg.lower() or "jvm" in error_msg.lower():
                result["error"] = "Camelot requires Java. Please install Java and ensure it's in your PATH."
            elif "ghostscript" in error_msg.lower():
                result["error"] = "Camelot requires Ghostscript. Please install Ghostscript."
            else:
                result["error"] = f"Failed to parse PDF with Camelot: {error_msg}"
        
        return result

