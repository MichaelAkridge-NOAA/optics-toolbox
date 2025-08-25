"""
Web interface for GCS Browser using Streamlit
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
    """Main web interface function"""
    try:
        st.set_page_config(
            page_title="GCS Bucket Browser & Downloader",
            page_icon="☁️",
            layout="wide"
        )
        
        st.title("☁️ Google Cloud Storage Browser & Downloader")
        st.markdown("Browse GCS buckets like a file tree and download files/folders with multiple methods")
        
        # Add debug info in expander
        with st.expander("🐛 Debug Info (click if app seems stuck)"):
            st.write("✅ Streamlit loaded successfully")
            st.write(f"🐍 Python version: {sys.version}")
            st.write("📦 Checking dependencies...")
            
            try:
                import pandas
                st.write("✅ pandas imported")
            except ImportError as e:
                st.error(f"❌ pandas import failed: {e}")
                
            try:
                import gcsfs
                st.write("✅ gcsfs imported")
            except ImportError as e:
                st.error(f"❌ gcsfs import failed: {e}")
                
            try:
                import google.cloud.storage
                st.write("✅ google-cloud-storage imported")
            except ImportError as e:
                st.error(f"❌ google-cloud-storage import failed: {e}")
        
    except Exception as e:
        st.error(f"Error in main setup: {e}")
        st.text("Full traceback:")
        st.text(traceback.format_exc())
        st.stop()
    
    st.write("🔄 Initializing session state...")
    
    # Initialize session state with error handling
    try:
        if 'browser' not in st.session_state:
            st.write("🔧 Creating GCS Browser instance...")
            # Add a progress bar to show it's working
            progress = st.progress(0)
            progress.progress(25)
            
            st.session_state.browser = GCSBrowser()
            progress.progress(100)
            st.write("✅ GCS Browser created successfully")
            progress.empty()  # Remove progress bar
        
        if 'connected' not in st.session_state:
            st.session_state.connected = False
        
        if 'current_path' not in st.session_state:
            st.session_state.current_path = []
            
        st.write("✅ Session state initialized")
        
        # Clear the debug messages after successful init (keep page clean)
        if st.session_state.get('debug_cleared', False) is False:
            st.session_state.debug_cleared = True
            # st.rerun()  # Uncomment this line if you want to hide debug messages after init
        
    except Exception as e:
        st.error(f"Error initializing GCS Browser: {e}")
        st.text("Full traceback:")
        st.text(traceback.format_exc())
        st.stop()
    
    browser = st.session_state.browser
    st.write("🎯 Loading main interface...")
    
    # Add a simple test to make sure everything is working
    st.write("🧪 Testing basic functionality...")
    test_container = st.empty()
    
    try:
        # Test that we can access browser methods
        test_bucket = "test"
        # This shouldn't make any network calls, just test object access
        _ = browser.current_bucket
        test_container.success("✅ Browser object working correctly")
    except Exception as e:
        test_container.error(f"❌ Browser object test failed: {e}")
        st.stop()
    
    st.write("🚀 Rendering interface components...")
    
    # Sidebar for connection and settings
    with st.sidebar:
        st.header("🔧 Connection Settings")
        
        # Connection options
        auth_method = st.radio(
            "Authentication:",
            ["Anonymous (public buckets only)", "Service Account Key", "Default Credentials"],
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
            use_anon = auth_method == "Anonymous (public buckets only)"
            
            with st.spinner("Connecting to GCS..."):
                if browser.connect(use_anonymous=use_anon, credentials_path=credentials_path):
                    st.session_state.connected = True
                    st.success("✅ Connected!")
                    st.rerun()
                else:
                    st.error("❌ Connection failed")
        
        if st.session_state.connected:
            st.success("🟢 Connected to GCS")
        else:
            st.warning("🔴 Not connected")
        
        st.divider()
        
        # Download tools detection
        st.header("🛠️ Available Tools")
        tools = detect_download_tools()
        
        for tool, available in tools.items():
            status = "✅" if available else "❌"
            st.write(f"{status} {tool}")
        
        if not any(tools.values()):
            st.warning("No download tools detected. Consider installing gsutil or gcloud SDK.")
        
        st.divider()
        
        # Download settings
        st.header("⬇️ Download Settings")
        
        default_dest = str(Path.home() / "Downloads" / "gcs_downloads")
        destination_folder = st.text_input(
            "Default destination:",
            value=default_dest,
            help="Where to download files by default"
        )
        
        preferred_method = st.selectbox(
            "Preferred download method:",
            ["gsutil" if tools.get('gsutil') else None,
             "gcsfs (Python)",
             "gcloud" if tools.get('gcloud') else None],
            help="Choose your preferred download method"
        )
        
        parallel_downloads = st.checkbox("Parallel downloads", value=True)
    
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
            - Limited to publicly accessible data
            """)
            
        with col2:
            st.markdown("""
            ### Authenticated Access
            - Access private buckets
            - Upload service account JSON key
            - Full read/write permissions (based on account)
            """)
        
        st.markdown("## 📋 Features")
        
        features = [
            "🌳 Tree-like bucket browsing",
            "📁 Folder size calculation",
            "⬇️ Multiple download methods (gsutil, gcsfs, gcloud)",
            "📊 Download progress tracking",
            "🔄 Resume interrupted downloads",
            "🌐 Cross-platform (Windows/Linux/MacOS)",
            "⚡ Parallel downloads for speed",
            "🎯 Selective file/folder downloads"
        ]
        
        for feature in features:
            st.write(feature)
        
        return
    
    # Browser interface
    col_nav, col_main = st.columns([1, 3])
    
    with col_nav:
        st.header("📂 Browser")
        
        # Bucket selection
        if not browser.current_bucket:
            st.subheader("📦 Select Bucket")
            buckets = browser.list_buckets()
            
            # Show common public buckets for easy access
            st.markdown("**🌐 Public NOAA Data:**")
            public_buckets = [
                "nmfs_odp_pifsc"
            ]
            
            for bucket in public_buckets:
                if st.button(f"📁 {bucket}", key=f"pub_{bucket}"):
                    browser.current_bucket = bucket
                    st.session_state.current_path = [bucket]
                    st.rerun()
            
            st.divider()
            
            if buckets:
                st.markdown("**🔐 Your Buckets:**")
                selected_bucket = st.selectbox("Available buckets:", [""] + buckets)
                if selected_bucket and st.button("Open Bucket"):
                    browser.current_bucket = selected_bucket
                    st.session_state.current_path = [selected_bucket]
                    st.rerun()
            
            st.markdown("**✏️ Manual Entry:**")
            manual_bucket = st.text_input(
                "Enter bucket name:", 
                placeholder="my-bucket-name",
                help="Enter any bucket name you have access to"
            )
            if manual_bucket and st.button("🚀 Open Bucket", type="primary"):
                browser.current_bucket = manual_bucket
                st.session_state.current_path = [manual_bucket]
                st.rerun()
        else:
            # Current path breadcrumb
            st.write("**Current path:**")
            for i, part in enumerate(st.session_state.current_path):
                if st.button(part, key=f"breadcrumb_{i}"):
                    # Navigate to this level
                    st.session_state.current_path = st.session_state.current_path[:i+1]
                    browser.current_prefix = "/".join(st.session_state.current_path[1:])
                    browser.items_cache.clear()  # Clear cache
                    st.rerun()
            
            if len(st.session_state.current_path) > 1 and st.button("⬆️ Up"):
                st.session_state.current_path.pop()
                browser.current_prefix = "/".join(st.session_state.current_path[1:])
                browser.items_cache.clear()
                st.rerun()
    
    with col_main:
        if browser.current_bucket:
            st.header(f"📁 {browser.current_bucket}")
            
            # Current prefix
            if browser.current_prefix:
                st.write(f"**📍 /{browser.current_prefix}**")
            
            # Load and display items
            with st.spinner("Loading..."):
                items = browser.list_items(browser.current_bucket, browser.current_prefix)
            
            if not items:
                st.info("📭 No items found in this location")
            else:
                # Items table with selection
                st.subheader(f"📋 Items ({len(items)})")
                
                # Selection controls
                col_select, col_download = st.columns([2, 1])
                
                with col_select:
                    if st.button("Select All"):
                        browser.selected_items = {item.path for item in items}
                        st.rerun()
                    
                    if st.button("Clear Selection"):
                        browser.selected_items.clear()
                        st.rerun()
                
                with col_download:
                    if browser.selected_items:
                        st.write(f"🎯 {len(browser.selected_items)} selected")
                    
                    if st.button("⬇️ Download Selected", 
                                disabled=not browser.selected_items,
                                type="primary"):
                        st.session_state.show_download_dialog = True
                
                # Items display
                for item in items:
                    col_check, col_icon, col_name, col_size, col_action = st.columns([1, 1, 4, 2, 2])
                    
                    with col_check:
                        is_selected = item.path in browser.selected_items
                        if st.checkbox("", value=is_selected, key=f"select_{item.path}"):
                            browser.selected_items.add(item.path)
                        else:
                            browser.selected_items.discard(item.path)
                    
                    with col_icon:
                        if item.type == "folder":
                            st.write("📁")
                        else:
                            # File icon based on extension
                            ext = Path(item.name).suffix.lower()
                            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                                st.write("🖼️")
                            elif ext in ['.txt', '.md', '.csv']:
                                st.write("📄")
                            elif ext in ['.zip', '.tar', '.gz']:
                                st.write("📦")
                            else:
                                st.write("📄")
                    
                    with col_name:
                        st.write(f"**{item.name}**")
                        if item.modified:
                            # Handle both datetime objects and strings
                            if hasattr(item.modified, 'strftime'):
                                mod_str = item.modified.strftime('%Y-%m-%d %H:%M')
                            else:
                                mod_str = str(item.modified)
                            st.caption(f"Modified: {mod_str}")
                    
                    with col_size:
                        if item.type == "file":
                            st.write(item.size_human)
                        else:
                            if st.button("📊", key=f"size_{item.path}", 
                                        help="Calculate folder size"):
                                with st.spinner("Calculating..."):
                                    folder_size = browser.get_folder_size(
                                        browser.current_bucket, 
                                        item.path.replace(f"{browser.current_bucket}/", "")
                                    )
                                    if folder_size > 0:
                                        size_item = GCSItem("", "", "folder", size=folder_size)
                                        st.success(f"Size: {size_item.size_human}")
                    
                    with col_action:
                        if item.type == "folder":
                            if st.button("🔍", key=f"open_{item.path}", help="Open folder"):
                                # Navigate into folder
                                folder_name = item.name
                                st.session_state.current_path.append(folder_name)
                                if browser.current_prefix:
                                    browser.current_prefix = f"{browser.current_prefix}/{folder_name}"
                                else:
                                    browser.current_prefix = folder_name
                                browser.items_cache.clear()
                                st.rerun()
                        else:
                            if st.button("⬇️", key=f"download_{item.path}", help="Download file"):
                                # Quick download single file
                                with st.spinner(f"Downloading {item.name}..."):
                                    dest_folder = Path(destination_folder)
                                    dest_folder.mkdir(parents=True, exist_ok=True)
                                    
                                    success = download_with_gcsfs(
                                        browser, 
                                        f"gs://{item.path}",
                                        str(dest_folder)
                                    )
                                    
                                    if success:
                                        st.success(f"✅ Downloaded to {dest_folder}")
                                    else:
                                        st.error("❌ Download failed")
        
        # Download dialog
        if st.session_state.get('show_download_dialog', False):
            st.subheader("⬇️ Download Selected Items")
            
            selected_paths = list(browser.selected_items)
            
            col_dest, col_method = st.columns(2)
            
            with col_dest:
                download_dest = st.text_input(
                    "Destination folder:",
                    value=destination_folder,
                    key="download_destination"
                )
            
            with col_method:
                available_methods = [m for m in ["gsutil", "gcsfs", "gcloud"] 
                                   if tools.get(m, m == "gcsfs")]
                method = st.selectbox(
                    "Download method:",
                    available_methods,
                    key="download_method_select"
                )
            
            # Estimate download size
            total_size = 0
            for path in selected_paths:
                if not path.endswith('/'):  # File
                    try:
                        info = browser.fs.info(f"gs://{path}")
                        total_size += info.get('size', 0)
                    except:
                        pass
            
            if total_size > 0:
                size_item = GCSItem("", "", "", size=total_size)
                st.info(f"📊 Estimated download size: {size_item.size_human}")
            
            col_start, col_cancel = st.columns(2)
            
            with col_start:
                if st.button("🚀 Start Download", type="primary"):
                    # Start download process
                    dest_path = Path(download_dest)
                    dest_path.mkdir(parents=True, exist_ok=True)
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, path in enumerate(selected_paths):
                        status_text.text(f"Downloading {path}...")
                        
                        if method == "gsutil":
                            success = download_with_gsutil(
                                f"gs://{path}",
                                str(dest_path),
                                recursive=True
                            )
                        else:
                            success = download_with_gcsfs(
                                browser,
                                f"gs://{path}",
                                str(dest_path)
                            )
                        
                        progress_bar.progress((i + 1) / len(selected_paths))
                        
                        if not success:
                            st.error(f"❌ Failed to download {path}")
                    
                    status_text.text("✅ Download completed!")
                    st.session_state.show_download_dialog = False
                    browser.selected_items.clear()
            
            with col_cancel:
                if st.button("❌ Cancel"):
                    st.session_state.show_download_dialog = False
                    st.rerun()


def run_web_app():
    """Entry point for the gcs-browser-web command"""
    import subprocess
    import sys
    import os
    
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
