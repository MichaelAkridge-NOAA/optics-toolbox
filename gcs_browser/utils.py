"""
Utility functions for GCS Browser
"""

import os
import subprocess
import platform
from pathlib import Path
from typing import Dict, Optional


def detect_download_tools() -> Dict[str, bool]:
    """Detect available download tools"""
    tools = {}
    
    # Check for gsutil
    try:
        subprocess.run(['gsutil', '--version'], capture_output=True, check=True)
        tools['gsutil'] = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        tools['gsutil'] = False
    
    # Check for gcloud
    try:
        subprocess.run(['gcloud', '--version'], capture_output=True, check=True)
        tools['gcloud'] = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        tools['gcloud'] = False
    
    # Check for rsync (Linux/MacOS)
    if platform.system() != 'Windows':
        try:
            subprocess.run(['rsync', '--version'], capture_output=True, check=True)
            tools['rsync'] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            tools['rsync'] = False
    else:
        tools['rsync'] = False
        # Check for robocopy (Windows)
        try:
            subprocess.run(['robocopy', '/?'], capture_output=True)
            tools['robocopy'] = True
        except FileNotFoundError:
            tools['robocopy'] = False
    
    return tools


def download_with_gsutil(source: str, destination: str, recursive: bool = True, 
                        parallel: bool = True, progress_callback=None) -> bool:
    """Download using gsutil"""
    try:
        cmd = ['gsutil']
        
        if parallel:
            cmd.extend(['-m'])  # Multi-threaded
        
        cmd.append('cp')
        
        if recursive:
            cmd.append('-r')
        
        cmd.extend([source, destination])
        
        # Run with progress monitoring
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break
            if output and progress_callback:
                progress_callback(output.strip())
        
        return process.returncode == 0
        
    except Exception as e:
        print(f"gsutil download failed: {e}")
        return False


def download_with_gcsfs(browser, source_path: str, destination: str, 
                       progress_callback=None) -> bool:
    """Download using gcsfs (Python library)"""
    try:
        if not browser.fs:
            return False
        
        # Check if source is file or directory
        try:
            info = browser.fs.info(source_path)
            is_file = info.get('type') == 'file'
        except:
            is_file = False
        
        if is_file:
            # Single file download
            dest_path = Path(destination)
            if dest_path.is_dir():
                filename = source_path.split('/')[-1]
                dest_path = dest_path / filename
            
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            with browser.fs.open(source_path, 'rb') as src, open(dest_path, 'wb') as dst:
                # Copy with progress
                chunk_size = 8192 * 1024  # 8MB chunks
                total_size = info.get('size', 0)
                downloaded = 0
                
                while True:
                    chunk = src.read(chunk_size)
                    if not chunk:
                        break
                    dst.write(chunk)
                    downloaded += len(chunk)
                    
                    if progress_callback:
                        progress_callback(downloaded, total_size)
        else:
            # Directory download
            files = browser.fs.glob(f"{source_path}/**")
            dest_base = Path(destination)
            
            for file_path in files:
                try:
                    file_info = browser.fs.info(file_path)
                    if file_info.get('type') != 'file':
                        continue
                    
                    # Calculate relative path
                    rel_path = file_path.replace(source_path, '').lstrip('/')
                    dest_file = dest_base / rel_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Download file
                    with browser.fs.open(file_path, 'rb') as src, open(dest_file, 'wb') as dst:
                        chunk_size = 1024 * 1024  # 1MB chunks
                        while True:
                            chunk = src.read(chunk_size)
                            if not chunk:
                                break
                            dst.write(chunk)
                    
                    if progress_callback:
                        progress_callback(f"Downloaded: {rel_path}")
                        
                except Exception as e:
                    print(f"Failed to download {file_path}: {e}")
                    continue
        
        return True
        
    except Exception as e:
        print(f"gcsfs download failed: {e}")
        return False


def sync_with_rsync(source: str, destination: str, dry_run: bool = False, 
                   delete: bool = False, verbose: bool = False) -> bool:
    """Sync using rsync (requires gsutil to first sync to temp location)"""
    if platform.system() == 'Windows':
        print("❌ rsync not available on Windows. Use gsutil or robocopy instead.")
        return False
    
    try:
        # First, use gsutil to sync to a temp location
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"🔄 First syncing {source} to temporary location...")
            if not download_with_gsutil(source, temp_dir, recursive=True, verbose=verbose):
                return False
            
            # Then use rsync to sync to final destination
            cmd = ['rsync', '-av']
            
            if dry_run:
                cmd.append('--dry-run')
            
            if delete:
                cmd.append('--delete')
            
            if verbose:
                cmd.append('--progress')
            
            # Find the actual source in temp dir
            temp_source = Path(temp_dir)
            actual_sources = list(temp_source.iterdir())
            
            if len(actual_sources) == 1:
                cmd.extend([str(actual_sources[0]) + '/', destination])
            else:
                cmd.extend([str(temp_source) + '/', destination])
            
            print(f"🔄 Running rsync: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=not verbose, text=True)
            
            if result.returncode == 0:
                print(f"✅ Successfully synced to {destination}")
                return True
            else:
                print(f"❌ rsync failed with return code {result.returncode}")
                if result.stderr:
                    print(f"Error: {result.stderr}")
                return False
                
    except Exception as e:
        print(f"❌ rsync sync failed: {e}")
        return False
