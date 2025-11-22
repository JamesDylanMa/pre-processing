"""
Configuration settings for the document preprocessing service
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
CACHE_DIR = BASE_DIR / "cache"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'pdf': ['.pdf'],
    'word': ['.doc', '.docx'],
    'excel': ['.xls', '.xlsx', '.xlsm'],
    'powerpoint': ['.ppt', '.pptx'],
    'text': ['.txt', '.md'],
    'image': ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
}

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODELS = {
    "multimodal": ["llava", "bakllava", "llava-phi3"],
    "text": ["llama3", "mistral", "phi3"],
    "recommended": "llava"  # Recommended multimodal model
}

# Processing settings
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ENABLE_ENSEMBLE = True
ENABLE_COMPARISON = True

# Output formats
OUTPUT_FORMATS = ['json', 'md']


