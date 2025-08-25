#!/usr/bin/env python3
"""
Test script to verify the gcs-browser-web entry point works correctly
"""

import sys
import subprocess
from pathlib import Path

def test_installation():
    """Test if the package is installed correctly"""
    try:
        import gcs_browser
        print("✅ gcs_browser package imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import gcs_browser: {e}")
        return False
    
    try:
        from gcs_browser.web import main, run_web_app
        print("✅ web module functions imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import web functions: {e}")
        return False
    
    return True

def test_entry_point():
    """Test the console script entry point"""
    try:
        result = subprocess.run([
            sys.executable, "-c", 
            "from gcs_browser.web import run_web_app; print('Entry point accessible')"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Entry point function accessible")
            return True
        else:
            print(f"❌ Entry point test failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Entry point test timed out")
        return False
    except Exception as e:
        print(f"❌ Entry point test error: {e}")
        return False

def main():
    print("🧪 Testing optics-toolbox web interface setup...")
    print()
    
    if not test_installation():
        print("\n❌ Installation test failed!")
        sys.exit(1)
    
    if not test_entry_point():
        print("\n❌ Entry point test failed!")
        sys.exit(1)
    
    print("\n✅ All tests passed!")
    print("\n💡 To start the web interface:")
    print("   gcs-browser-web")
    print("\n💡 Alternative method:")
    print("   python -m streamlit run gcs_browser/web.py")

if __name__ == "__main__":
    main()
