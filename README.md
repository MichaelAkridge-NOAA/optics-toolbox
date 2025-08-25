# Optics Toolbox - GCS Bucket Browser & Downloader

A user-friendly, cross-platform tool to browse Google Cloud Storage buckets like a file tree, select folders/files to download, and sync them to local destinations using various methods.

![Platform Support](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)

## Features

### Browser Features
- **Tree-like browsing**: Navigate GCS buckets like a local file system
- **File/folder selection**: Multi-select files and folders for batch operations
- **Size calculation**: Get folder sizes and file information
- **Search and filtering**: Find files by name, type, or size
- **Breadcrumb navigation**: Easy navigation with clickable path elements

### ⬇Download Options
- **Multiple methods**: gsutil, gcsfs (Python), gcloud, rsync
- **Resume support**: Resume interrupted downloads
- **Progress tracking**: Real-time download progress and estimates
- **Parallel downloads**: Multi-threaded downloads for speed
- **Bandwidth limiting**: Control download speed
- **Selective sync**: Download only what you need

### Cross-Platform Support
- **Windows**: Works with PowerShell, Command Prompt, and WSL
- **Linux**: Full native support with all features
- **macOS**: Complete compatibility

### 🔐 Authentication Options
- **Anonymous access**: Browse public buckets without authentication
- **Service Account**: Use JSON key files for private access
- **Default credentials**: Use gcloud default credentials
- **Multiple projects**: Switch between different GCP projects

## 🚀 Quick Start

### Installation
```bash
# Try this first - works on most systems
pip install git+https://github.com/MichaelAkridge-NOAA/optics-toolbox.git
```

### For Cloud Workstations / Managed Environments

```bash
# Simple one-command install (handles everything automatically)
curl -sSL https://raw.githubusercontent.com/MichaelAkridge-NOAA/optics-toolbox/main/install-simple.sh | bash
```

#### Alternative: Docker Installation (Recommended for Complex Cloud Environments)

If you encounter Python environment issues or want the most reliable installation:

```bash
# One-command Docker setup (installs Docker if needed)
curl -sSL https://raw.githubusercontent.com/MichaelAkridge-NOAA/optics-toolbox/main/cloud_docker_install.sh | bash
```

This will:
- Install Docker if not present
- Build and run the optics-toolbox in a container
- Set up helper scripts (`gcs-browser` and `gcs-browser-web`)
- Access the web interface at http://localhost:8501

#### Then activate and use (for non-Docker install):

1. Activate the virtual environment:
```
   source optics-env/bin/activate
```
2. Use the tools:
```
   gcs-browser browse gs://nmfs_odp_pifsc/
   gcs-browser-web
```

3. For private buckets, authenticate first:
```
   gcloud auth login
   # or: gcloud init --no-launch-browser
```

## Startup
###  Web Interface
```bash
# Start the web interface
gcs-browser-web
```

#### Accessing on Google Cloud Workstation
When running on Google Cloud Workstation, the app will start but won't auto-open in browser. You'll see:
```
Local URL: http://localhost:8501
Network URL: http://10.88.0.3:8501
External URL: http://34.48.90.74:8501
```

**To access the web interface:**
1. **VS Code method**: In VS Code, go to `Ports` tab → Click `Forward a Port` → Enter `8501`
2. **Direct access**: Click the "Open in Browser" button that appears in VS Code
3. **Manual**: Copy the `External URL` (e.g., http://34.48.90.74:8501) and open in new browser tab

#### Accessing on Local Machine
```bash
# Open your browser to http://localhost:8501
# Should open automatically
```

### Quick CLI Usage
```bash
# Command line interface
gcs-browser browse gs://nmfs_odp_pifsc/
gcs-browser download gs://nmfs_odp_pifsc/some-folder/ ./downloads/
```

## Usage Examples

### Command Line Interface

#### Basic Browsing
```bash
# List contents of a bucket
gcs-browser browse gs://public-bucket/

# Browse subfolder
gcs-browser browse gs://public-bucket/subfolder/

# Verbose output
gcs-browser browse gs://bucket/ --verbose
```

#### Downloads
```bash
# Download single file
gcs-browser download gs://bucket/file.txt ./downloads/

# Download folder with gsutil (fast)
gcs-browser download gs://bucket/data/ ./local-data/ --method gsutil --parallel

# Download with Python library (no external tools needed)
gcs-browser download gs://bucket/data/ ./local-data/ --method gcsfs

# Dry run (see what would be downloaded)
gcs-browser download gs://bucket/data/ ./local-data/ --dry-run
```

#### Syncing
```bash
# Sync folder (like rsync)
gcs-browser sync gs://bucket/data/ ./local-data/

# Sync with delete (remove local files not in bucket)
gcs-browser sync gs://bucket/data/ ./local-data/ --delete

# Dry run sync
gcs-browser sync gs://bucket/data/ ./local-data/ --dry-run
```

#### Authentication
```bash
# Use service account key
gcs-browser browse gs://private-bucket/ --credentials /path/to/key.json

# Use anonymous access (default for public buckets)
gcs-browser browse gs://public-bucket/ --anonymous

# Use gcloud default credentials (after gcloud auth login)
gcs-browser browse gs://private-bucket/
```

#### Setting up Google Cloud Authentication
```bash
# Interactive setup (opens browser)
gcloud auth login

# Headless/remote setup (no browser)
gcloud init --no-launch-browser

# Set default project
gcloud config set project YOUR_PROJECT_ID

# Verify authentication
gcloud auth list
```

### Python API
```python
from gcs_browser import GCSBrowser

# Create browser instance
browser = GCSBrowser()
browser.connect(use_anonymous=True)

# List items in a bucket
items = browser.list_items("nmfs_odp_pifsc", "PIFSC/ESD/ARP/")

for item in items:
    print(f"{item.type}: {item.name} ({item.size_human})")

# Download a file
from gcs_browser.utils import download_with_gcsfs
download_with_gcsfs(browser, "gs://nmfs_odp_pifsc/some-file.txt", "./downloads/")
```

## 📂 Public Datasets Examples

### NOAA Data
```bash
gcs-browser browse gs://nmfs_odp_pifsc/
# Ocean and fisheries data, AI datasets, coral imagery
```

## 🛠️ Download Methods Comparison

**Recommendations:**
- **gsutil**: Best overall performance and features
- **gcsfs**: No external dependencies, good for simple use cases
- **rsync**: Best for Linux users who need advanced syncing

## External Tools (Optional)

**Google Cloud SDK** (includes gsutil and gcloud):

**Windows:**
1. Download from: https://cloud.google.com/sdk/docs/install
2. Run installer and follow setup wizard
3. Restart command prompt
4. Run: `gcloud auth login` (or `gcloud init --no-launch-browser` for headless/remote setups)

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install google-cloud-sdk

# CentOS/RHEL  
sudo yum install google-cloud-sdk

# Or using snap
sudo snap install google-cloud-sdk --classic

# Authenticate
gcloud auth login
# Or for headless/remote setups:
gcloud init --no-launch-browser
```

**macOS:**
```bash
# Using Homebrew
brew install --cask google-cloud-sdk

# Authenticate
gcloud auth login
# Or for headless/remote setups:
gcloud init --no-launch-browser
```

## Troubleshooting / Common Issues

**"gcs-browser-web shows warning about streamlit run"**
This is normal - the command automatically launches Streamlit. If it doesn't open your browser:
- Copy the URL shown (usually http://localhost:8501)  
- Open it manually in your browser

**"Web interface won't load on Google Cloud Workstation"**
The Streamlit app starts but you need to access it through port forwarding:
1. In VS Code: Go to `Ports` tab → `Forward a Port` → Enter `8501`
2. Click the "Open in Browser" button in VS Code
3. Or use the External URL shown (e.g., http://YOUR-IP:8501)

**"Web interface stuck at loading screen"**
If the interface opens but stays stuck loading:

**Quick fixes to try:**
1. **Check the terminal** where `gcs-browser-web` is running for error messages
2. **Force refresh** the page: `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)  
3. **Try incognito/private mode** to rule out browser cache issues
4. **Restart the web interface**:
   ```bash
   # Press Ctrl+C to stop, then restart
   source optics-env/bin/activate  # if using virtual env
   gcs-browser-web
   ```

**For Google Cloud Workstation specifically:**
1. **Check browser console**: Press `F12` → Console tab → look for JavaScript errors
2. **Try different browser**: Chrome vs Firefox vs Safari
3. **Check if app actually loaded**: Look for "Debug Info" expandable section on the page
4. **Verify dependencies**:
   ```bash
   source optics-env/bin/activate
   python -c "import streamlit, gcs_browser, pandas, gcsfs; print('✅ All dependencies OK')"
   ```
5. **If import errors**, reinstall:
   ```bash
   pip install --upgrade git+https://github.com/MichaelAkridge-NOAA/optics-toolbox.git
   ```

**"gsutil not found"**
- Install Google Cloud SDK
- Or use `--method gcsfs` to use Python libraries only

**"Access Denied"**
- For public buckets: Use `--anonymous` flag
- For private buckets: Provide credentials with `--credentials path/to/key.json`
- Check bucket permissions

**"Download Failed"**
- Check internet connection
- Verify bucket/file exists: `gcs-browser browse gs://bucket/path/`
- Try different download method: `--method gcsfs`

## Configuration

Example config file: `gcs_browser/config.example.json`
- Copy this file to `config.json` and edit as needed for your environment. The app will use your custom config if present.

----------
#### Disclaimer
This repository is a scientific product and is not official communication of the National Oceanic and Atmospheric Administration, or the United States Department of Commerce. All NOAA GitHub project content is provided on an ‘as is’ basis and the user assumes responsibility for its use. Any claims against the Department of Commerce or Department of Commerce bureaus stemming from the use of this GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by the Department of Commerce. The Department of Commerce seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by DOC or the United States Government.

#### License
- Details in the [LICENSE.md](./LICENSE.md) file.