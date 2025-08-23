#!/usr/bin/env python3
"""
GCS Bucket Browser & Downloader - CLI Interface
"""

import sys
import argparse
import subprocess
from pathlib import Path

from .core import GCSBrowser, GCSItem
from .utils import detect_download_tools, download_with_gsutil, download_with_gcsfs, sync_with_rsync


class GCSCLIBrowser(GCSBrowser):
    """CLI version of GCS Browser with print-based output"""
    
    def __init__(self, use_anonymous=True, credentials_path=None):
        super().__init__()
        self.connect(use_anonymous, credentials_path)


def main():
    parser = argparse.ArgumentParser(
        description="GCS Bucket Browser & Downloader - CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list-buckets
  %(prog)s browse gs://my-bucket/
  %(prog)s browse gs://my-bucket/subfolder/
  %(prog)s download gs://my-bucket/file.txt ./downloads/
  %(prog)s download gs://my-bucket/folder/ ./downloads/ --method gsutil
  %(prog)s sync gs://my-bucket/data/ ./local-data/ --delete
        """
    )
    
    parser.add_argument('command', choices=['list-buckets', 'browse', 'download', 'sync'],
                       help='Command to execute')
    parser.add_argument('source', nargs='?', help='GCS path (gs://bucket/path/)')
    parser.add_argument('destination', nargs='?', help='Local destination path')
    
    parser.add_argument('--credentials', '-c', help='Path to service account JSON key')
    parser.add_argument('--anonymous', '-a', action='store_true', 
                       help='Use anonymous access (default: True)')
    parser.add_argument('--method', '-m', choices=['gsutil', 'gcsfs', 'rsync'],
                       default='gsutil', help='Download method (default: gsutil)')
    parser.add_argument('--parallel', '-p', action='store_true', default=True,
                       help='Use parallel downloads (default: True)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without doing it')
    parser.add_argument('--delete', action='store_true',
                       help='Delete files in destination that don\'t exist in source (sync only)')
    
    args = parser.parse_args()
    
    # Detect available tools
    tools = detect_download_tools()
    
    if args.verbose:
        print("🛠️  Available tools:")
        for tool, available in tools.items():
            status = "✅" if available else "❌"
            print(f"   {status} {tool}")
        print()
    
    # Validate method availability
    if args.method == 'gsutil' and not tools['gsutil']:
        print("❌ gsutil not available. Install Google Cloud SDK or use --method gcsfs")
        return 1
    
    if args.method == 'rsync' and not tools['rsync']:
        print("❌ rsync not available on this platform. Use gsutil or gcsfs instead.")
        return 1
    
    # Initialize browser
    use_anon = args.anonymous or not args.credentials
    browser = GCSCLIBrowser(use_anonymous=use_anon, credentials_path=args.credentials)
    
    # Execute command
    if args.command == 'list-buckets':
        print("📋 Available buckets:")
        buckets = browser.list_buckets()
        if buckets:
            for bucket in buckets:
                print(f"  📁 {bucket}")
        else:
            print("  (none found or using anonymous access)")
    
    elif args.command == 'browse':
        if not args.source:
            print("❌ Source GCS path required for browse command")
            return 1
        
        print(f"📂 Browsing: {args.source}")
        
        # Parse GCS path
        if not args.source.startswith('gs://'):
            print(f"❌ Invalid GCS path: {args.source}. Must start with gs://")
            return 1
        
        path = args.source[5:]  # Remove 'gs://'
        parts = path.split('/', 1)
        bucket = parts[0]
        prefix = parts[1] if len(parts) > 1 else ""
        
        items = browser.list_items(bucket, prefix)
        
        if not items:
            print("  📭 No items found")
        else:
            print(f"  Found {len(items)} items:\n")
            
            # Calculate column widths
            max_name_len = max(len(item.name) for item in items)
            max_size_len = max(len(item.size_human) for item in items if item.type == 'file')
            max_size_len = max(max_size_len, 8) if max_size_len else 8
            
            # Header
            print(f"  {'Type':<6} {'Name':<{max_name_len}} {'Size':<{max_size_len}} {'Modified'}")
            print(f"  {'-'*6} {'-'*max_name_len} {'-'*max_size_len} {'-'*19}")
            
            # Items
            for item in items:
                icon = "📁" if item.type == "folder" else "📄"
                size_str = item.size_human if item.type == "file" else "-"
                
                if item.modified:
                    if hasattr(item.modified, 'strftime'):
                        modified_str = item.modified.strftime('%Y-%m-%d %H:%M')
                    else:
                        modified_str = str(item.modified)[:19]  # Truncate if string
                else:
                    modified_str = "-"
                
                print(f"  {icon:<6} {item.name:<{max_name_len}} {size_str:<{max_size_len}} {modified_str}")
    
    elif args.command == 'download':
        if not args.source or not args.destination:
            print("❌ Both source and destination required for download command")
            return 1
        
        if args.dry_run:
            print(f"🔍 Dry run - would download {args.source} to {args.destination}")
            return 0
        
        print(f"⬇️  Downloading {args.source} to {args.destination} using {args.method}")
        
        if args.method == 'gsutil':
            success = download_with_gsutil(
                args.source, args.destination, 
                recursive=True, parallel=args.parallel
            )
        else:  # gcsfs
            success = download_with_gcsfs(browser, args.source, args.destination)
        
        return 0 if success else 1
    
    elif args.command == 'sync':
        if not args.source or not args.destination:
            print("❌ Both source and destination required for sync command")
            return 1
        
        if args.dry_run:
            print(f"🔍 Dry run - would sync {args.source} to {args.destination}")
            if args.delete:
                print("   (with --delete option)")
            return 0
        
        print(f"🔄 Syncing {args.source} to {args.destination}")
        
        if args.method == 'rsync':
            success = sync_with_rsync(
                args.source, args.destination, 
                dry_run=args.dry_run, delete=args.delete, verbose=args.verbose
            )
        else:
            # Use gsutil for sync
            cmd = ['gsutil', '-m', 'rsync', '-r']
            if args.delete:
                cmd.append('-d')
            if args.verbose:
                cmd.append('-v')
            cmd.extend([args.source, args.destination])
            
            print(f"🚀 Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=not args.verbose, text=True)
            success = result.returncode == 0
            
            if success:
                print(f"✅ Successfully synced to {args.destination}")
            else:
                print(f"❌ Sync failed with return code {result.returncode}")
                if result.stderr:
                    print(f"Error: {result.stderr}")
        
        return 0 if success else 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
