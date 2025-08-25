#!/usr/bin/env python3
"""
Alternative streamlit launcher that works better on Windows
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Launch streamlit with the web interface"""
    
    # Find the web.py file
    try:
        import gcs_browser.web
        web_module_path = Path(gcs_browser.web.__file__)
    except ImportError:
        print("❌ Could not import gcs_browser.web")
        print("💡 Make sure the package is installed: pip install git+https://github.com/MichaelAkridge-NOAA/optics-toolbox.git")
        sys.exit(1)
    
    print("🚀 Starting GCS Browser Web Interface...")
    print("📱 Access at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    # Launch streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        str(web_module_path),
        "--server.address", "0.0.0.0",
        "--server.port", "8501"
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Try running directly:")
        print(f"   python -m streamlit run {web_module_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()
