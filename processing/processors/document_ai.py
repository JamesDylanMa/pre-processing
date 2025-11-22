"""
Document AI processor using various AI models
"""
from typing import Dict, Optional
import json
from processing.processors.base_processor import BaseProcessor


class DocumentAIProcessor(BaseProcessor):
    """AI-powered document processor"""
    
    def __init__(self, model_name: Optional[str] = None):
        super().__init__("document_ai")
        self.model_name = model_name
    
    def process(self, file_path: str, file_type: str, **kwargs) -> Dict:
        """
        Process document with AI enhancement
        
        Args:
            file_path: Path to file
            file_type: Type of file
            **kwargs: Additional options (e.g., ai_model, enhancement_type)
            
        Returns:
            Enhanced processed result
        """
        # First parse the document
        parsed_result = self.parse_document(file_path, file_type)
        
        if "error" in parsed_result:
            return parsed_result
        
        # 프로세서 이름 명시적으로 설정 (parser와 구분)
        parsed_result["processor"] = self.name
        # 원본 parser 정보는 유지하되, processor로 구분
        if "parser" in parsed_result:
            parsed_result["original_parser"] = parsed_result["parser"]
        
        # Add AI processing metadata
        parsed_result["ai_processing"] = {
            "model": kwargs.get("ai_model", self.model_name),
            "enhancement_type": kwargs.get("enhancement_type", "basic"),
            "processed": True
        }
        
        # Basic AI enhancements (can be extended with actual AI calls)
        if parsed_result.get("text"):
            text = parsed_result["text"]
            
            # Add basic statistics
            parsed_result["statistics"] = {
                "total_characters": len(text),
                "total_words": len(text.split()),
                "total_sentences": len([s for s in text.split('.') if s.strip()]),
                "estimated_reading_time_minutes": len(text.split()) / 200  # Average reading speed
            }
        
        # 텍스트 정제 및 향상 (간단한 전처리)
        if parsed_result.get("text"):
            # 공백 정규화
            parsed_result["text"] = " ".join(parsed_result["text"].split())
            # 문장 단위로 정리
            sentences = [s.strip() for s in parsed_result["text"].split('.') if s.strip()]
            parsed_result["cleaned_text"] = ". ".join(sentences) + ("." if sentences else "")
        
        return parsed_result


