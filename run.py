"""
Main entry point for the document preprocessing service
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import streamlit.web.cli as stcli
    
    # Run Streamlit app
    sys.argv = [
        "streamlit",
        "run",
        str(project_root / "frontend" / "streamlit_app.py"),
        "--server.port=8501",
        "--server.address=0.0.0.0"
    ]
    
    sys.exit(stcli.main())


