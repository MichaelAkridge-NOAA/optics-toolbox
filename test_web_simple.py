#!/usr/bin/env python3
"""
Simple test version of the GCS Browser web app
This strips out complexity to help debug hanging issues
"""

import streamlit as st
import sys
import time
import traceback

def main():
    """Minimal test web interface"""
    st.set_page_config(
        page_title="GCS Browser Test",
        page_icon="🧪",
        layout="wide"
    )
    
    st.title("🧪 GCS Browser - Test Version")
    st.write("If you can see this, Streamlit is working!")
    
    st.write(f"🐍 Python version: {sys.version}")
    st.write(f"⏰ Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test importing our modules
    st.subheader("📦 Testing Imports")
    
    try:
        import pandas as pd
        st.success("✅ pandas imported successfully")
        st.write(f"   Version: {pd.__version__}")
    except Exception as e:
        st.error(f"❌ pandas import failed: {e}")
    
    try:
        import gcsfs
        st.success("✅ gcsfs imported successfully")
        st.write(f"   Version: {gcsfs.__version__}")
    except Exception as e:
        st.error(f"❌ gcsfs import failed: {e}")
    
    try:
        from google.cloud import storage
        st.success("✅ google-cloud-storage imported successfully")
    except Exception as e:
        st.error(f"❌ google-cloud-storage import failed: {e}")
    
    # Test our own modules
    try:
        from gcs_browser.core import GCSBrowser
        st.success("✅ GCSBrowser imported successfully")
    except Exception as e:
        st.error(f"❌ GCSBrowser import failed: {e}")
        st.text("Full error:")
        st.code(traceback.format_exc())
    
    try:
        from gcs_browser.utils import detect_download_tools
        tools = detect_download_tools()
        st.success("✅ Utils imported successfully")
        st.write("Available tools:", tools)
    except Exception as e:
        st.error(f"❌ Utils import failed: {e}")
        st.text("Full error:")
        st.code(traceback.format_exc())
    
    st.subheader("🔧 Basic Functionality Test")
    
    if st.button("Test GCS Connection"):
        with st.spinner("Testing connection..."):
            try:
                from gcs_browser.core import GCSBrowser
                browser = GCSBrowser()
                st.write("✅ Browser object created")
                
                # Test anonymous connection
                success = browser.connect(use_anonymous=True)
                if success:
                    st.success("✅ Anonymous connection successful!")
                    
                    # Try to access a public bucket
                    try:
                        import gcsfs
                        fs = gcsfs.GCSFileSystem(token='anon')
                        
                        # Test listing a known public bucket
                        test_bucket = "gcp-public-data-sentinel-2"
                        files = fs.ls(test_bucket, detail=False)[:5]  # Just first 5
                        
                        st.success(f"✅ Successfully listed {len(files)} items from public bucket")
                        for f in files:
                            st.write(f"   📁 {f}")
                            
                    except Exception as e:
                        st.warning(f"⚠️  Could not test bucket listing: {e}")
                        
                else:
                    st.error("❌ Connection failed")
                    
            except Exception as e:
                st.error(f"❌ Test failed: {e}")
                st.text("Full error:")
                st.code(traceback.format_exc())
    
    st.subheader("💡 Next Steps")
    if st.button("Launch Full App"):
        st.info("If this test works, try running the full app with: gcs-browser-web")
    
    st.markdown("""
    ### 🐛 Troubleshooting
    
    **If this test page doesn't load:**
    - Streamlit itself has issues
    - Check Docker container is running
    - Check port 8501 is accessible
    
    **If imports fail:**
    - Dependencies not installed correctly
    - Virtual environment issues
    - Package conflicts
    
    **If connection test fails:**
    - Network connectivity issues
    - Google Cloud API access blocked
    - Firewall/proxy issues
    """)

if __name__ == "__main__":
    main()
