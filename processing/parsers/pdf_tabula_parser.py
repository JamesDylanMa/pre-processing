"""
PDF document parser using Tabula - Good for table extraction
"""
from typing import Dict, List
from pathlib import Path
try:
    import tabula
    TABULA_AVAILABLE = True
except ImportError:
    TABULA_AVAILABLE = False


class TabulaParser:
    """Parse PDF documents using Tabula (table extraction)"""
    
    def __init__(self):
        self.name = "tabula_parser"
    
    def parse(self, file_path: str) -> Dict:
        """
        Parse PDF file using Tabula
        
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
        
        if not TABULA_AVAILABLE:
            result["error"] = "tabula-py library not available. Install with: pip install tabula-py"
            return result
        
        try:
            import pandas as pd
            
            # Extract tables from all pages
            dfs = tabula.read_pdf(file_path, pages='all', multiple_tables=True)
            
            result["metadata"]["method"] = "tabula"
            result["metadata"]["total_tables"] = len(dfs)
            
            all_text = []
            for i, df in enumerate(dfs):
                # Convert DataFrame to list of lists
                table_data = df.fillna("").values.tolist()
                table_text = "\n".join([" | ".join([str(cell) for cell in row]) for row in table_data])
                
                result["tables"].append({
                    "table_number": i + 1,
                    "data": table_data,
                    "columns": df.columns.tolist(),
                    "shape": list(df.shape)
                })
                
                all_text.append(table_text)
            
            result["text"] = "\n\n--- Table ---\n\n".join(all_text)
            
            # Create pages structure
            if dfs:
                # Estimate pages (tabula doesn't provide page info directly)
                result["metadata"]["total_pages"] = len(dfs)  # Approximation
                for i in range(len(dfs)):
                    result["pages"].append({
                        "page_number": i + 1,
                        "text": all_text[i] if i < len(all_text) else "",
                        "tables": [result["tables"][i]] if i < len(result["tables"]) else []
                    })
        
        except Exception as e:
            result["error"] = f"Failed to parse PDF with Tabula: {str(e)}"
        
        return result

