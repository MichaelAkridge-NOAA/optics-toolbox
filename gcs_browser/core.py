"""
Core classes and functionality for GCS Browser
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime

try:
    from dateutil.parser import parse as parse_date
    HAS_DATEUTIL = True
except ImportError:
    HAS_DATEUTIL = False

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

import pandas as pd
import gcsfs
from google.cloud import storage
from google.api_core import exceptions as gcs_exceptions


@dataclass
class GCSItem:
    """Represents a GCS object or folder"""
    name: str
    path: str
    type: str  # 'file' or 'folder'
    size: int = 0
    modified: Optional[datetime] = None
    etag: Optional[str] = None
    
    @property
    def size_human(self) -> str:
        """Human readable file size"""
        if self.size == 0:
            return "0 B"
        
        sizes = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(self.size)
        while size >= 1024.0 and i < len(sizes) - 1:
            size /= 1024.0
            i += 1
        return f"{size:.1f} {sizes[i]}"


@dataclass
class DownloadJob:
    """Represents a download job"""
    source_path: str
    destination: str
    total_size: int = 0
    downloaded_size: int = 0
    status: str = "pending"  # pending, running, completed, error
    error_msg: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def progress_percent(self) -> float:
        if self.total_size == 0:
            return 0.0
        return (self.downloaded_size / self.total_size) * 100


class GCSBrowser:
    """Main GCS Browser class"""
    
    def __init__(self):
        self.fs = None
        self.client = None
        self.current_bucket = ""
        self.current_prefix = ""
        self.items_cache = {}
        self.selected_items: Set[str] = set()
        self.download_jobs: List[DownloadJob] = []
    
    def _safe_parse_date(self, date_value):
        """Safely parse date from various formats"""
        if not date_value:
            return None
        
        if isinstance(date_value, datetime):
            return date_value
        
        if isinstance(date_value, str):
            if HAS_DATEUTIL:
                try:
                    # Try parsing with dateutil
                    return parse_date(date_value)
                except:
                    # If that fails, return the string as-is for display
                    return date_value
            else:
                # Fallback: try basic ISO format parsing
                try:
                    # Handle common GCS datetime format: 2023-12-01T12:34:56.789Z
                    if 'T' in date_value and date_value.endswith('Z'):
                        # Remove Z and microseconds if present
                        clean_date = date_value.rstrip('Z')
                        if '.' in clean_date:
                            clean_date = clean_date.split('.')[0]
                        return datetime.fromisoformat(clean_date)
                    else:
                        return datetime.fromisoformat(date_value)
                except:
                    # If parsing fails, return the string for display
                    return date_value
        
        return date_value
        
    def connect(self, use_anonymous=True, credentials_path=None):
        """Connect to GCS"""
        try:
            if use_anonymous:
                self.fs = gcsfs.GCSFileSystem(token='anon')
                self.client = storage.Client.create_anonymous_client()
            else:
                if credentials_path:
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
                self.fs = gcsfs.GCSFileSystem()
                self.client = storage.Client()
            return True
        except Exception as e:
            if HAS_STREAMLIT and 'st' in globals():
                st.error(f"Failed to connect to GCS: {e}")
            else:
                print(f"❌ Failed to connect to GCS: {e}")
            return False
    
    def list_buckets(self) -> List[str]:
        """List available buckets"""
        try:
            if self.client and hasattr(self.client, '_credentials') and self.client._credentials:
                # Only list buckets if we have valid credentials
                return [bucket.name for bucket in self.client.list_buckets()]
            else:
                # For anonymous access, we can't list buckets
                if 'st' in globals():
                    st.info("ℹ️ Anonymous access - cannot list buckets. Enter bucket name manually below.")
                else:
                    print("⚠️  Anonymous access - cannot list all buckets")
                    print("💡 Common public buckets you can try:")
                    print("   - nmfs_odp_pifsc (NOAA fisheries data)")
                return []
        except Exception as e:
            if 'st' in globals():
                st.warning(f"Could not list buckets: {e}")
                st.info("💡 Try entering a bucket name manually or use authentication.")
            else:
                print(f"⚠️  Could not list buckets: {e}")
                print("💡 Try using specific bucket names or authenticate with credentials")
            return []
    
    def list_items(self, bucket: str, prefix: str = "") -> List[GCSItem]:
        """List items in bucket/prefix"""
        if not self.fs:
            return []
            
        cache_key = f"{bucket}/{prefix}"
        if cache_key in self.items_cache:
            return self.items_cache[cache_key]
        
        try:
            items = []
            path = f"{bucket}/{prefix}".rstrip("/")
            
            # Get detailed listing
            gcs_items = self.fs.ls(path, detail=True)
            
            # Process folders and files
            folders_seen = set()
            
            for item in gcs_items:
                item_path = item['name']
                relative_path = item_path.replace(f"{bucket}/", "")
                
                if prefix:
                    if not relative_path.startswith(prefix):
                        continue
                    relative_path = relative_path[len(prefix):].lstrip("/")
                
                if not relative_path:
                    continue
                
                # Handle folders
                if item['type'] == 'directory':
                    name = relative_path.rstrip("/").split("/")[-1]
                    if name not in folders_seen:
                        items.append(GCSItem(
                            name=name,
                            path=item_path,
                            type="folder",
                            size=0,
                            modified=self._safe_parse_date(item.get('updated'))
                        ))
                        folders_seen.add(name)
                else:
                    # Handle files
                    if "/" in relative_path:
                        # File in subfolder - create folder entry if not exists
                        folder_name = relative_path.split("/")[0]
                        if folder_name not in folders_seen:
                            folder_path = f"{bucket}/{prefix}/{folder_name}".replace("//", "/")
                            items.append(GCSItem(
                                name=folder_name,
                                path=folder_path,
                                type="folder",
                                size=0,
                                modified=None
                            ))
                            folders_seen.add(folder_name)
                    else:
                        # Direct file
                        items.append(GCSItem(
                            name=relative_path,
                            path=item_path,
                            type="file",
                            size=item.get('size', 0),
                            modified=self._safe_parse_date(item.get('updated')),
                            etag=item.get('etag')
                        ))
            
            # Sort: folders first, then files, both alphabetically
            items.sort(key=lambda x: (x.type != "folder", x.name.lower()))
            
            self.items_cache[cache_key] = items
            return items
            
        except Exception as e:
            if HAS_STREAMLIT and 'st' in globals():
                st.error(f"Error listing items: {e}")
            else:
                print(f"❌ Error listing items: {e}")
            return []
    
    def get_folder_size(self, bucket: str, prefix: str) -> int:
        """Calculate total size of a folder"""
        try:
            total_size = 0
            path = f"{bucket}/{prefix}".rstrip("/")
            
            # Use glob to get all files recursively
            pattern = f"{path}/**"
            files = self.fs.glob(pattern)
            
            for file_path in files:
                try:
                    info = self.fs.info(file_path)
                    if info.get('type') == 'file':
                        total_size += info.get('size', 0)
                except:
                    continue
                    
            return total_size
        except Exception as e:
            if 'st' in globals():
                st.warning(f"Could not calculate folder size: {e}")
            else:
                print(f"⚠️  Could not calculate folder size: {e}")
            return 0
