"""
Web interface for GCS Browser using Streamlit
"""

import streamlit as st
from pathlib import Path
from typing import Set

from .core import GCSBrowser, GCSItem, DownloadJob
from .utils import detect_download_tools, download_with_gsutil, download_with_gcsfs


def main():
    """Main web interface function"""
    st.set_page_config(
        page_title="GCS Bucket Browser & Downloader",
        page_icon="☁️",
        layout="wide"
    )
    
    st.title("☁️ Google Cloud Storage Browser & Downloader")
    st.markdown("Browse GCS buckets like a file tree and download files/folders with multiple methods")
    
    # Initialize session state
    if 'browser' not in st.session_state:
        st.session_state.browser = GCSBrowser()
    
    if 'connected' not in st.session_state:
        st.session_state.connected = False
    
    if 'current_path' not in st.session_state:
        st.session_state.current_path = []
    
    browser = st.session_state.browser
    
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


if __name__ == "__main__":
    main()
