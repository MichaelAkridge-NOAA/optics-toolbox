#!/bin/bash
# Quick install script for cloud workstations
# Usage: curl -sSL https://raw.githubusercontent.com/MichaelAkridge-NOAA/optics-toolbox/main/install-cloud.sh | bash

set -e

echo "🌩️ Installing Optics Toolbox for Cloud Workstation..."

# Check if we're in an externally managed environment
if pip install --help | grep -q "externally-managed-environment" 2>/dev/null; then
    echo "📦 Detected managed environment, using virtual environment..."
    
    # Create virtual environment
    python3 -m venv optics-env
    source optics-env/bin/activate
    
    echo "✅ Virtual environment created and activated"
    echo "💡 To use later, run: source optics-env/bin/activate"
else
    echo "📦 Standard environment detected"
fi

# Install the package
echo "⬬ Installing optics-toolbox..."
pip install git+https://github.com/MichaelAkridge-NOAA/optics-toolbox.git

echo "🎉 Installation complete!"
echo ""
echo "🚀 Quick start:"
echo "   gcs-browser browse gs://nmfs_odp_pifsc/"
echo "   gcs-browser-web"
echo ""
echo "🔧 For private buckets, authenticate first:"
echo "   gcloud auth login"
echo "   # or: gcloud init --no-launch-browser"
