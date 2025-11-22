"""
Ensemble processor that combines multiple processors
"""
from typing import Dict, List, Optional
from processing.processors.base_processor import BaseProcessor
from processing.processors.document_ai import DocumentAIProcessor
from processing.comparison import ResultComparator


class EnsembleProcessor(BaseProcessor):
    """Combine results from multiple processors"""
    
    def __init__(self, processors: Optional[List[str]] = None):
        super().__init__("ensemble_processor")
        self.processors = processors or ["pdf_parser", "document_ai"]
        self.comparator = ResultComparator()
    
    def process(self, file_path: str, file_type: str, **kwargs) -> Dict:
        """
        Process document using multiple processors and combine results
        
        Args:
            file_path: Path to file
            file_type: Type of file
            **kwargs: Additional options
            
        Returns:
            Combined result from all processors
        """
        results = []
        
        # Process with base parser
        base_result = self.parse_document(file_path, file_type)
        if "error" not in base_result:
            results.append(base_result)
        
        # Process with AI processor if enabled
        if "document_ai" in self.processors:
            ai_processor = DocumentAIProcessor()
            ai_result = ai_processor.process(file_path, file_type, **kwargs)
            if "error" not in ai_result:
                results.append(ai_result)
        
        # Combine results
        ensemble_result = self._combine_results(results)
        
        # Add comparison if multiple results
        if len(results) > 1:
            comparison = self.comparator.compare_results(results)
            ensemble_result["comparison"] = comparison
        
        ensemble_result["ensemble_info"] = {
            "processors_used": self.processors,
            "total_results_combined": len(results)
        }
        
        return ensemble_result
    
    def _combine_results(self, results: List[Dict]) -> Dict:
        """Combine multiple processing results"""
        if not results:
            return {"error": "No results to combine"}
        
        combined = {
            "ensemble_result": True,
            "source_results": len(results),
            "combined_text": "",
            "combined_metadata": {},
            "all_tables": [],
            "all_pages": []
        }
        
        # Combine text (deduplicate similar content)
        texts = []
        for result in results:
            text = result.get("text", "")
            if text:
                texts.append(text)
        
        combined["combined_text"] = "\n\n---\n\n".join(texts)
        
        # Combine metadata
        all_metadata = {}
        for result in results:
            if "metadata" in result:
                all_metadata.update(result["metadata"])
        combined["combined_metadata"] = all_metadata
        
        # Combine tables
        for result in results:
            if "tables" in result:
                combined["all_tables"].extend(result["tables"])
            if "sheets" in result:
                combined["all_tables"].extend(result["sheets"])
        
        # Combine pages
        for result in results:
            if "pages" in result:
                combined["all_pages"].extend(result["pages"])
            if "slides" in result:
                combined["all_pages"].extend(result["slides"])
        
        return combined


