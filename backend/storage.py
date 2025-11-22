"""
Storage management for processed results
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from config import OUTPUT_DIR


class StorageManager:
    """Manage storage of processed results"""
    
    def __init__(self):
        self.output_dir = OUTPUT_DIR
    
    def save_result(self, result_data: Dict, file_id: str, 
                   processor_name: str, format: str = 'json', 
                   original_filename: Optional[str] = None) -> Path:
        """
        Save processing result
        
        Args:
            result_data: Processed data dictionary
            file_id: Original file ID
            processor_name: Name of the processor used
            format: Output format ('json' or 'md')
            original_filename: Original filename for better naming
            
        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 파일명 생성: 원본파일명_파서명 형식
        if original_filename:
            # 확장자 제거
            base_name = Path(original_filename).stem
            # 특수문자 제거 및 정리
            safe_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')
            filename = f"{safe_name}_{processor_name}.{format}"
        else:
            filename = f"{file_id}_{processor_name}_{timestamp}.{format}"
        
        file_path = self.output_dir / filename
        
        if format == 'json':
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
        elif format == 'md':
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self._dict_to_markdown(result_data))
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return file_path
    
    def load_result(self, file_path: Path) -> Dict:
        """Load a saved result"""
        if file_path.suffix == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            raise ValueError(f"Cannot load format: {file_path.suffix}")
    
    def get_results_for_file(self, file_id: str) -> List[Path]:
        """Get all result files for a given file ID"""
        return list(self.output_dir.glob(f"{file_id}_*"))
    
    def _dict_to_markdown(self, data: Dict, level: int = 0) -> str:
        """Convert dictionary to markdown format"""
        md_lines = []
        indent = "  " * level
        
        for key, value in data.items():
            if isinstance(value, dict):
                md_lines.append(f"{indent}## {key}")
                md_lines.append(self._dict_to_markdown(value, level + 1))
            elif isinstance(value, list):
                md_lines.append(f"{indent}### {key}")
                for item in value:
                    if isinstance(item, dict):
                        md_lines.append(self._dict_to_markdown(item, level + 1))
                    else:
                        md_lines.append(f"{indent}- {item}")
            else:
                md_lines.append(f"{indent}**{key}**: {value}")
        
        return "\n".join(md_lines)
    
    def save_comparison_result(self, comparison_data: Dict, file_id: str) -> Path:
        """Save comparison result"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{file_id}_comparison_{timestamp}.json"
        file_path = self.output_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(comparison_data, f, ensure_ascii=False, indent=2)
        
        return file_path


