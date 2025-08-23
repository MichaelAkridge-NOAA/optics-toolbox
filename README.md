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

#### For Cloud Workstations / Managed Environments

**Super Quick (One Command):**
```bash
# Automated install script - handles everything
curl -sSL https://raw.githubusercontent.com/MichaelAkridge-NOAA/optics-toolbox/main/install-cloud.sh | bash
```

**Manual Install:**
```bash
# Create a virtual environment (works everywhere)
python3 -m venv optics-env
source optics-env/bin/activate
pip install git+https://github.com/MichaelAkridge-NOAA/optics-toolbox.git

# Ready to use!
gcs-browser browse gs://nmfs_odp_pifsc/
gcs-browser-web
```

#### Standard Installation
```bash
# Try this first - works on most systems
pip install git+https://github.com/MichaelAkridge-NOAA/optics-toolbox.git
```

### Installation Issues & Solutions

#### Alternative Methods (if above doesn't work)

**Option A: pipx (Isolated App Install)**
```bash
# Install as a standalone application
sudo apt install pipx  # or: pip install --user pipx
pipx ensurepath
pipx install git+https://github.com/MichaelAkridge-NOAA/optics-toolbox.git

# Commands available system-wide
gcs-browser browse gs://nmfs_odp_pifsc/
```

**Option B: System Override (Cloud Workstations)**
```bash
# If virtual env isn't preferred on temporary cloud instances
pip install git+https://github.com/MichaelAkridge-NOAA/optics-toolbox.git --break-system-packages
```

**What's included:**
- CLI tools: `gcs-browser` and `gcs-browser-web` 
- Web interface with Streamlit
- All core functionality for browsing and downloading
- Performance optimizations

### Web Interface
```bash
# Start the web interface
gcs-browser-web
# Open your browser to http://localhost:8501
```

The web interface provides:
- **Direct access to NOAA PIFSC bucket** with one click
- **Manual bucket entry** for any other buckets
- **Tree navigation** with breadcrumbs
- **Multi-file/folder selection** and download
- **Progress tracking** and error handling

### Quick Usage
```bash
# Command line interface
gcs-browser browse gs://nmfs_odp_pifsc/
gcs-browser download gs://nmfs_odp_pifsc/some-folder/ ./downloads/

# Web interface
gcs-browser-web
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

## Troubleshooting

### Common Issues

**"externally-managed-environment" Error**
This occurs on newer Linux systems (Ubuntu 22.04+, Debian 12+) that prevent system-wide pip installs:
```bash
# Recommended: Use virtual environment
python3 -m venv optics-env && source optics-env/bin/activate
pip install git+https://github.com/MichaelAkridge-NOAA/optics-toolbox.git

# Alternative: Use pipx
pipx install git+https://github.com/MichaelAkridge-NOAA/optics-toolbox.git

# Last resort: Override (not recommended)
pip install git+https://github.com/MichaelAkridge-NOAA/optics-toolbox.git --break-system-packages
```

**"Import gcsfs could not be resolved"**
```bash
pip install gcsfs google-cloud-storage
```

**"RequestsDependencyWarning: Unable to find acceptable character detection"**
```bash
pip install charset-normalizer
```

**"gcs-browser-web shows warning about streamlit run"**
This is normal - the command automatically launches Streamlit. If it doesn't open your browser:
- Copy the URL shown (usually http://localhost:8501)  
- Open it manually in your browser

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

Copy this file to `config.json` and edit as needed for your environment. The app will use your custom config if present.

## 🤝 Contributing

### Development Setup
```bash
git clone https://github.com/MichaelAkridge-NOAA/optics-toolbox.git
cd optics-toolbox
pip install -e ".[dev]"  # Install in development mode with dev dependencies
```

----------
#### Disclaimer
This repository is a scientific product and is not official communication of the National Oceanic and Atmospheric Administration, or the United States Department of Commerce. All NOAA GitHub project content is provided on an ‘as is’ basis and the user assumes responsibility for its use. Any claims against the Department of Commerce or Department of Commerce bureaus stemming from the use of this GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by the Department of Commerce. The Department of Commerce seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by DOC or the United States Government.

#### License
- Details in the [LICENSE.md](./LICENSE.md) file.