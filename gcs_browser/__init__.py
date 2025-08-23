"""
GCS Bucket Browser & Downloader

A user-friendly, cross-platform tool to browse Google Cloud Storage buckets 
like a file tree, select folders/files to download, and sync them to local 
destinations using various methods.

Features:
- Tree-like bucket browsing
- Cross-platform (Windows/Linux/macOS)
- Multiple download methods (gsutil, gcloud, gcsfs)
- Progress tracking and resume capabilities
- Web interface and CLI
- Bandwidth limiting options
"""

__version__ = "1.0.0"
__author__ = "Michael Akridge, NOAA"
__email__ = "michael.akridge@noaa.gov"
__description__ = "User-friendly Google Cloud Storage bucket browser and downloader"

from .core import GCSBrowser, GCSItem, DownloadJob
from .utils import detect_download_tools, download_with_gsutil, download_with_gcsfs

__all__ = [
    "GCSBrowser",
    "GCSItem", 
    "DownloadJob",
    "detect_download_tools",
    "download_with_gsutil",
    "download_with_gcsfs",
]
