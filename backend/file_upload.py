"""
File upload handling module
"""
import os
import shutil
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
import uuid

from config import UPLOAD_DIR, MAX_FILE_SIZE, ALLOWED_EXTENSIONS
from utils.file_utils import get_file_hash, get_file_type, is_allowed_file


class FileUploadHandler:
    """Handle file uploads and validation"""
    
    def __init__(self):
        self.upload_dir = UPLOAD_DIR
        self.max_size = MAX_FILE_SIZE
    
    def save_uploaded_file(self, uploaded_file, session_id: Optional[str] = None) -> Dict:
        """
        Save uploaded file and return metadata
        
        Args:
            uploaded_file: Streamlit uploaded file object
            session_id: Optional session ID for grouping files
            
        Returns:
            Dict with file metadata
        """
        if uploaded_file is None:
            raise ValueError("No file provided")
        
        # Validate file size
        if uploaded_file.size > self.max_size:
            raise ValueError(f"File size exceeds maximum allowed size of {self.max_size / (1024*1024):.1f}MB")
        
        # Validate file extension
        if not is_allowed_file(uploaded_file.name, ALLOWED_EXTENSIONS):
            raise ValueError(f"File type not supported: {uploaded_file.name}")
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        file_type = get_file_type(uploaded_file.name)
        
        # Create session directory if provided
        if session_id:
            session_dir = self.upload_dir / session_id
            session_dir.mkdir(exist_ok=True)
            file_path = session_dir / f"{file_id}_{uploaded_file.name}"
        else:
            file_path = self.upload_dir / f"{file_id}_{uploaded_file.name}"
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Generate file hash
        file_hash = get_file_hash(str(file_path))
        
        # Return metadata
        metadata = {
            "file_id": file_id,
            "original_name": uploaded_file.name,
            "file_path": str(file_path),
            "file_type": file_type,
            "file_size": uploaded_file.size,
            "file_hash": file_hash,
            "upload_time": datetime.now().isoformat(),
            "session_id": session_id
        }
        
        return metadata
    
    def get_file_path(self, file_id: str, session_id: Optional[str] = None) -> Optional[Path]:
        """Get file path by file ID"""
        if session_id:
            session_dir = self.upload_dir / session_id
            for file_path in session_dir.glob(f"{file_id}_*"):
                return file_path
        else:
            for file_path in self.upload_dir.glob(f"{file_id}_*"):
                return file_path
        return None
    
    def delete_file(self, file_id: str, session_id: Optional[str] = None) -> bool:
        """Delete file by file ID"""
        file_path = self.get_file_path(file_id, session_id)
        if file_path and file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def cleanup_session(self, session_id: str):
        """Clean up all files in a session"""
        session_dir = self.upload_dir / session_id
        if session_dir.exists():
            shutil.rmtree(session_dir)


