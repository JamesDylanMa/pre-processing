"""
Ollama integration for multi-modal document processing
"""
import requests
import base64
from typing import Dict, Optional, List
from pathlib import Path
import json

from config import OLLAMA_BASE_URL, OLLAMA_MODELS


class OllamaProcessor:
    """Process documents using Ollama multi-modal models"""
    
    def __init__(self, model_name: Optional[str] = None):
        self.base_url = OLLAMA_BASE_URL
        self.model = model_name or OLLAMA_MODELS["recommended"]
        self.available_models = self._get_available_models()
    
    def _get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
        except Exception:
            pass
        return []
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def process_text(self, text: str, prompt: str = "Extract and summarize the key information from this document:") -> Dict:
        """
        Process text using Ollama
        
        Args:
            text: Text to process
            prompt: Prompt for the model
            
        Returns:
            Processed result
        """
        if not self.is_available():
            return {"error": "Ollama service not available"}
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{prompt}\n\n{text}",
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "model": self.model
                }
            else:
                return {"error": f"Ollama API error: {response.status_code}"}
        
        except Exception as e:
            return {"error": f"Failed to process with Ollama: {str(e)}"}
    
    def process_image(self, image_path: str, prompt: str = "Describe the content of this image in detail:") -> Dict:
        """
        Process image using Ollama multi-modal model
        
        Args:
            image_path: Path to image file
            prompt: Prompt for the model
            
        Returns:
            Processed result
        """
        if not self.is_available():
            return {"error": "Ollama service not available"}
        
        # Check if model supports vision
        if not any(model in self.model.lower() for model in ["llava", "bakllava", "vision"]):
            return {"error": f"Model {self.model} does not support vision"}
        
        try:
            # Encode image
            image_base64 = self._encode_image(image_path)
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "images": [image_base64],
                    "stream": False
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "model": self.model,
                    "image_path": image_path
                }
            else:
                return {"error": f"Ollama API error: {response.status_code}"}
        
        except Exception as e:
            return {"error": f"Failed to process image with Ollama: {str(e)}"}
    
    def process_document(self, file_path: str, file_type: str, 
                        prompt: Optional[str] = None) -> Dict:
        """
        Process document using Ollama
        
        Args:
            file_path: Path to document
            file_type: Type of document
            prompt: Custom prompt (optional)
            
        Returns:
            Processed result
        """
        result = {
            "file_path": file_path,
            "file_type": file_type,
            "model": self.model,
            "ollama_processing": {}
        }
        
        # For images, use vision model
        if file_type == "image":
            default_prompt = "Extract all text and describe the visual content of this document image:"
            ollama_result = self.process_image(file_path, prompt or default_prompt)
            result["ollama_processing"] = ollama_result
        
        # For text-based documents, extract text first then process
        else:
            # This would need to integrate with parsers to extract text first
            # For now, return a placeholder
            result["ollama_processing"] = {
                "note": "Text extraction required before Ollama processing",
                "suggestion": "Use a parser first to extract text, then use process_text()"
            }
        
        return result
    
    def get_recommended_model(self) -> str:
        """Get recommended model for the task"""
        return OLLAMA_MODELS["recommended"]
    
    def list_models(self) -> List[str]:
        """List available models"""
        return self.available_models


