#!/usr/bin/env python3
"""
Simplified GCS Browser Web App
Strips out complex features to isolate hanging issues
"""

import streamlit as st
import sys
import traceback
from pathlib import Path

def main():
    """Simplified main web interface"""
    st.set_page_config(
        page_title="GCS Browser - Simple",
        page_icon="☁️",
        layout="wide"
    )
    
    st.title("☁️ GCS Browser - Simplified Version")
    st.write("This is a simplified version to help debug issues.")
    
    # Simple progress indicator
    st.write("✅ Streamlit loaded successfully")
    
    # Test imports with detailed error reporting
    st.subheader("📦 Checking Dependencies")
    
    imports_ok = True
    
    try:
        import pandas as pd
        st.success("✅ pandas imported")
    except ImportError as e:
        st.error(f"❌ pandas import failed: {e}")
        imports_ok = False
    
    try:
        import gcsfs
        st.success("✅ gcsfs imported")
    except ImportError as e:
        st.error(f"❌ gcsfs import failed: {e}")
        imports_ok = False
    
    try:
        from google.cloud import storage
        st.success("✅ google-cloud-storage imported")
    except ImportError as e:
        st.error(f"❌ google-cloud-storage import failed: {e}")
        imports_ok = False
    
    # Only proceed if basic imports work
    if not imports_ok:
        st.error("❌ Basic dependencies failed. Cannot continue.")
        return
    
    # Test our modules with better error handling
    st.subheader("🔧 Testing GCS Browser Components")
    
    try:
        from gcs_browser.core import GCSBrowser
        st.success("✅ GCSBrowser imported")
        
        # Very simple browser test - no network calls yet
        browser = GCSBrowser()
        st.success("✅ GCSBrowser object created")
        
    except Exception as e:
        st.error(f"❌ GCSBrowser setup failed: {e}")
        st.text("Full traceback:")
        st.code(traceback.format_exc())
        return
    
    # Simple connection interface
    st.subheader("🔌 Connection")
    
    # Initialize session state simply
    if 'connected' not in st.session_state:
        st.session_state.connected = False
    
    if not st.session_state.connected:
        if st.button("🔗 Connect (Anonymous)", type="primary"):
            with st.spinner("Connecting to GCS..."):
                try:
                    success = browser.connect(use_anonymous=True)
                    if success:
                        st.session_state.connected = True
                        st.success("✅ Connected successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Connection failed")
                except Exception as e:
                    st.error(f"❌ Connection error: {e}")
                    st.code(traceback.format_exc())
    else:
        st.success("🟢 Connected to GCS")
        
        # Very simple bucket interface
        st.subheader("📁 Browse Buckets")
        
        # Manual bucket entry only (no auto-listing that might hang)
        bucket_name = st.text_input(
            "Enter bucket name:",
            placeholder="nmfs_odp_pifsc",
            help="Try: nmfs_odp_pifsc (NOAA public data)"
        )
        
        if bucket_name and st.button("🔍 Browse Bucket"):
            with st.spinner(f"Loading {bucket_name}..."):
                try:
                    # Simple file listing
                    items = browser.list_items(bucket_name, "")
                    
                    if items:
                        st.success(f"✅ Found {len(items)} items")
                        
                        # Show first 10 items only to avoid overload
                        for item in items[:10]:
                            if item.type == "folder":
                                st.write(f"📁 {item.name}")
                            else:
                                st.write(f"📄 {item.name} ({item.size_human})")
                        
                        if len(items) > 10:
                            st.info(f"... and {len(items) - 10} more items")
                    else:
                        st.warning("No items found")
                        
                except Exception as e:
                    st.error(f"❌ Failed to list bucket contents: {e}")
                    st.code(traceback.format_exc())
        
        if st.button("🔌 Disconnect"):
            st.session_state.connected = False
            st.rerun()
    
    # Troubleshooting info
    st.divider()
    st.subheader("🛠️ Troubleshooting")
    
    with st.expander("System Information"):
        st.code(f"Python: {sys.version}")
        st.code(f"Platform: {sys.platform}")
        
        # Check if we're in Docker
        try:
            with open('/proc/1/cgroup', 'r') as f:
                if 'docker' in f.read():
                    st.info("🐳 Running inside Docker container")
        except:
            pass
    
    st.markdown("""
    ### If this simplified version works:
    - The issue is likely in the full app's complexity
    - Session state management
    - Too many UI components loading at once
    
    ### If this version also hangs:
    - Check Docker container logs
    - Network connectivity issues
    - Streamlit configuration problems
    """)


def run_simple_web_app():
    """Entry point for simplified web app"""
    import subprocess
    import sys
    
    # Get the path to this file
    web_script = __file__
    
    # Run streamlit with this script
    cmd = [sys.executable, "-m", "streamlit", "run", web_script]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()
