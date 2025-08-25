#!/usr/bin/env python3
"""
Improved GCS Browser Web App with better error handling and simpler initialization
"""

import streamlit as st
from pathlib import Path
from typing import Set
import sys
import traceback

try:
    from .core import GCSBrowser, GCSItem, DownloadJob
    from .utils import detect_download_tools, download_with_gsutil, download_with_gcsfs
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("This usually means dependencies are not installed correctly.")
    st.stop()


def main():
    """Improved main web interface function with better error handling"""
    try:
        st.set_page_config(
            page_title="GCS Bucket Browser & Downloader",
            page_icon="☁️",
            layout="wide"
        )
        
        st.title("☁️ Google Cloud Storage Browser & Downloader")
        st.markdown("Browse GCS buckets like a file tree and download files/folders with multiple methods")
        
    except Exception as e:
        st.error(f"Error in page setup: {e}")
        st.text("Full traceback:")
        st.text(traceback.format_exc())
        st.stop()
    
    # Simplified session state initialization
    if 'browser' not in st.session_state:
        try:
            with st.spinner("Initializing GCS Browser..."):
                st.session_state.browser = GCSBrowser()
        except Exception as e:
            st.error(f"Failed to initialize GCS Browser: {e}")
            st.text("Full traceback:")
            st.text(traceback.format_exc())
            st.stop()
    
    if 'connected' not in st.session_state:
        st.session_state.connected = False
    
    if 'current_path' not in st.session_state:
        st.session_state.current_path = []
    
    browser = st.session_state.browser
    
    # Sidebar for connection and settings
    with st.sidebar:
        st.header("🔧 Connection Settings")
        
        # Simplified connection options
        auth_method = st.radio(
            "Authentication:",
            ["Anonymous (public buckets)", "Service Account Key"],
            key="auth_method"
        )
        
        credentials_path = None
        if auth_method == "Service Account Key":
            uploaded_key = st.file_uploader(
                "Upload service account JSON key:",
                type=['json'],
                help="Upload your GCP service account key file"
            )
            if uploaded_key:
                # Save temporary file
                key_path = Path.cwd() / "temp_credentials.json"
                with open(key_path, 'wb') as f:
                    f.write(uploaded_key.read())
                credentials_path = str(key_path)
        
        # Connect button
        if st.button("🔌 Connect to GCS", type="primary"):
            use_anon = auth_method == "Anonymous (public buckets)"
            
            with st.spinner("Connecting to GCS..."):
                try:
                    success = browser.connect(use_anonymous=use_anon, credentials_path=credentials_path)
                    if success:
                        st.session_state.connected = True
                        st.success("✅ Connected!")
                        st.rerun()
                    else:
                        st.error("❌ Connection failed")
                except Exception as e:
                    st.error(f"❌ Connection error: {e}")
                    st.text(traceback.format_exc())
        
        if st.session_state.connected:
            st.success("🟢 Connected to GCS")
        else:
            st.warning("🔴 Not connected")
        
        st.divider()
        
        # Download tools detection (simplified)
        st.header("🛠️ Available Tools")
        try:
            tools = detect_download_tools()
            for tool, available in tools.items():
                status = "✅" if available else "❌"
                st.write(f"{status} {tool}")
        except Exception as e:
            st.warning(f"Could not detect tools: {e}")
    
    # Main interface
    if not st.session_state.connected:
        st.info("👈 Please connect to GCS using the sidebar to start browsing")
        
        # Show some helpful information
        st.markdown("## 🚀 Getting Started")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### Anonymous Access
            - Browse public GCS buckets
            - No authentication required
            - Try: `nmfs_odp_pifsc`
            """)
            
        with col2:
            st.markdown("""
            ### Authenticated Access
            - Access private buckets
            - Upload service account JSON key
            - Full permissions based on account
            """)
        
        return
    
    # Simplified browser interface
    col_nav, col_main = st.columns([1, 3])
    
    with col_nav:
        st.header("📂 Browser")
        
        # Bucket selection (simplified)
        if not browser.current_bucket:
            st.subheader("📦 Select Bucket")
            
            # Show suggested public buckets
            st.markdown("**🌐 Public NOAA Data:**")
            public_buckets = ["nmfs_odp_pifsc"]
            
            for bucket in public_buckets:
                if st.button(f"📁 {bucket}", key=f"pub_{bucket}"):
                    browser.current_bucket = bucket
                    st.session_state.current_path = [bucket]
                    st.rerun()
            
            st.divider()
            
            # Manual bucket entry
            st.markdown("**✏️ Manual Entry:**")
            manual_bucket = st.text_input(
                "Enter bucket name:", 
                placeholder="my-bucket-name"
            )
            if manual_bucket and st.button("🚀 Open Bucket", type="primary"):
                browser.current_bucket = manual_bucket
                st.session_state.current_path = [manual_bucket]
                st.rerun()
        else:
            # Current path breadcrumb (simplified)
            st.write("**Current path:**")
            st.write(" / ".join(st.session_state.current_path))
            
            if len(st.session_state.current_path) > 1 and st.button("⬆️ Up"):
                st.session_state.current_path.pop()
                browser.current_prefix = "/".join(st.session_state.current_path[1:])
                browser.items_cache.clear()
                st.rerun()
    
    with col_main:
        if browser.current_bucket:
            st.header(f"📁 {browser.current_bucket}")
            
            # Load and display items with better error handling
            try:
                with st.spinner("Loading..."):
                    items = browser.list_items(browser.current_bucket, browser.current_prefix)
                
                if not items:
                    st.info("📭 No items found in this location")
                else:
                    st.subheader(f"📋 Items ({len(items)})")
                    
                    # Simple items display (limit to first 50 to avoid overload)
                    display_items = items[:50]
                    
                    for item in display_items:
                        col_icon, col_name, col_size, col_action = st.columns([1, 4, 2, 2])
                        
                        with col_icon:
                            if item.type == "folder":
                                st.write("📁")
                            else:
                                st.write("📄")
                        
                        with col_name:
                            st.write(f"**{item.name}**")
                            if item.modified:
                                st.caption(f"Modified: {item.modified}")
                        
                        with col_size:
                            if item.type == "file":
                                st.write(item.size_human)
                        
                        with col_action:
                            if item.type == "folder":
                                if st.button("🔍", key=f"open_{item.path}", help="Open folder"):
                                    folder_name = item.name
                                    st.session_state.current_path.append(folder_name)
                                    if browser.current_prefix:
                                        browser.current_prefix = f"{browser.current_prefix}/{folder_name}"
                                    else:
                                        browser.current_prefix = folder_name
                                    browser.items_cache.clear()
                                    st.rerun()
                    
                    if len(items) > 50:
                        st.info(f"Showing first 50 items. Total: {len(items)}")
                        
            except Exception as e:
                st.error(f"❌ Failed to load items: {e}")
                st.text("Full traceback:")
                st.text(traceback.format_exc())


def run_web_app():
    """Entry point for the gcs-browser-web command"""
    import subprocess
    import sys
    import os
    
    # Get the path to this file
    web_script = __file__
    
    # Run streamlit with this script
    cmd = [sys.executable, "-m", "streamlit", "run", web_script, "--server.address", "0.0.0.0"]
    
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
