"""
File utility functions
"""
import os
import hashlib
from pathlib import Path
from typing import Optional
import mimetypes

def get_file_hash(file_path: str) -> str:
    """Generate MD5 hash for a file"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_file_type(file_path: str) -> Optional[str]:
    """Detect file type from extension"""
    ext = Path(file_path).suffix.lower()
    
    type_mapping = {
        '.pdf': 'pdf',
        '.doc': 'word', '.docx': 'word',
        '.xls': 'excel', '.xlsx': 'excel', '.xlsm': 'excel',
        '.ppt': 'powerpoint', '.pptx': 'powerpoint',
        '.txt': 'text', '.md': 'text',
        '.png': 'image', '.jpg': 'image', '.jpeg': 'image',
        '.gif': 'image', '.bmp': 'image'
    }
    
    return type_mapping.get(ext)

def is_allowed_file(filename: str, allowed_extensions: dict) -> bool:
    """Check if file extension is allowed"""
    ext = Path(filename).suffix.lower()
    for file_type, extensions in allowed_extensions.items():
        if ext in extensions:
            return True
    return False

def get_mime_type(file_path: str) -> str:
    """Get MIME type of a file"""
    return mimetypes.guess_type(file_path)[0] or 'application/octet-stream'

def ensure_directory(path: Path):
    """Ensure directory exists"""
    path.mkdir(parents=True, exist_ok=True)


