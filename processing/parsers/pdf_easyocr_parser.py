"""
PDF document parser using EasyOCR - Better alternative to Tesseract OCR
EasyOCR is a free, open-source OCR library that supports 80+ languages
"""
from typing import Dict, List
from pathlib import Path
try:
    import easyocr
    from pdf2image import convert_from_path
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False


class EasyOCRParser:
    """Parse PDF documents using EasyOCR (better OCR alternative)"""
    
    def __init__(self):
        self.name = "easyocr_parser"
        self.reader = None
        if EASYOCR_AVAILABLE:
            try:
                import torch
                # Check if CUDA is available for GPU acceleration
                use_gpu = torch.cuda.is_available()
                # Initialize EasyOCR reader (supports Korean and English)
                self.reader = easyocr.Reader(['ko', 'en'], gpu=use_gpu)
            except Exception:
                # If GPU is not available, it will use CPU
                try:
                    self.reader = easyocr.Reader(['ko', 'en'], gpu=False)
                except Exception:
                    self.reader = None
    
    def parse(self, file_path: str) -> Dict:
        """
        Parse PDF file using EasyOCR
        
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
        
        if not EASYOCR_AVAILABLE:
            result["error"] = "EasyOCR libraries not available. Install with: pip install easyocr pdf2image"
            return result
        
        if self.reader is None:
            result["error"] = "EasyOCR reader initialization failed"
            return result
        
        try:
            # Convert PDF to images
            images = convert_from_path(file_path)
            
            result["metadata"]["total_pages"] = len(images)
            result["metadata"]["method"] = "EasyOCR"
            result["metadata"]["languages"] = ["Korean", "English"]
            
            full_text = []
            for i, image in enumerate(images):
                # Extract text using EasyOCR
                ocr_results = self.reader.readtext(image)
                
                # Combine all detected text
                page_text = "\n".join([text for (bbox, text, confidence) in ocr_results])
                full_text.append(page_text)
                
                # Calculate average confidence
                confidences = [conf for (bbox, text, conf) in ocr_results if conf > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                page_data = {
                    "page_number": i + 1,
                    "text": page_text,
                    "tables": [],
                    "ocr_confidence": round(avg_confidence, 2),
                    "detected_texts": len(ocr_results)
                }
                result["pages"].append(page_data)
            
            result["text"] = "\n\n--- Page Break ---\n\n".join(full_text)
            result["metadata"]["is_scanned"] = True
            result["metadata"]["ocr_used"] = True
            result["metadata"]["ocr_engine"] = "EasyOCR"
        
        except Exception as e:
            result["error"] = f"Failed to parse PDF with EasyOCR: {str(e)}"
        
        return result

