"""
Curator processor using NeMo Curator-inspired text curation
"""
from typing import Dict, Optional
from processing.processors.base_processor import BaseProcessor
from processing.curation.text_curator import TextCurator


class CuratorProcessor(BaseProcessor):
    """Text curation processor inspired by NVIDIA NeMo Curator"""
    
    def __init__(self, enable_cleaning: bool = True, 
                 enable_quality_check: bool = True,
                 enable_language_detection: bool = True):
        super().__init__("curator_processor")
        self.curator = TextCurator()
        self.enable_cleaning = enable_cleaning
        self.enable_quality_check = enable_quality_check
        self.enable_language_detection = enable_language_detection
    
    def process(self, file_path: str, file_type: str, **kwargs) -> Dict:
        """
        Process document with text curation
        
        Args:
            file_path: Path to file
            file_type: Type of file
            **kwargs: Additional options
            
        Returns:
            Curated processed result
        """
        # First parse the document
        parsed_result = self.parse_document(file_path, file_type)
        
        if "error" in parsed_result:
            return parsed_result
        
        # Set processor name
        parsed_result["processor"] = self.name
        if "parser" in parsed_result:
            parsed_result["original_parser"] = parsed_result["parser"]
        
        # Extract text for curation
        text_to_curate = parsed_result.get("text", "")
        
        # If no direct text, try to extract from pages
        if not text_to_curate and parsed_result.get("pages"):
            text_to_curate = "\n".join([
                page.get("text", "") for page in parsed_result.get("pages", [])
            ])
        
        # Curate text
        if text_to_curate:
            curation_result = self.curator.curate_text(
                text_to_curate,
                enable_cleaning=self.enable_cleaning,
                enable_quality_check=self.enable_quality_check,
                enable_language_detection=self.enable_language_detection
            )
            
            # Update text with curated version
            parsed_result["text"] = curation_result["curated_text"]
            parsed_result["original_text"] = curation_result["original_text"]
            parsed_result["curation_metadata"] = curation_result["curation_metadata"]
            
            # Add curation statistics
            parsed_result["curation_stats"] = {
                "text_cleaned": self.enable_cleaning,
                "quality_assessed": self.enable_quality_check,
                "language_detected": self.enable_language_detection,
                "quality_score": curation_result["curation_metadata"].get("quality", {}).get("quality_score", 0),
                "detected_language": curation_result["curation_metadata"].get("language", {}).get("language", "unknown")
            }
        
        return parsed_result

