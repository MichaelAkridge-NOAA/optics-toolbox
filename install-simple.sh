#!/bin/bash
# Simplified install script for Google Cloud Workstation and similar environments
# Usage: curl -sSL https://raw.githubusercontent.com/MichaelAkridge-NOAA/optics-toolbox/main/install-simple.sh | bash

set -e

echo "🌩️ Installing Optics Toolbox for Cloud Workstation..."
echo "🔧 This script will install system packages and set up a virtual environment"
echo ""

# Function to install system dependencies
install_deps() {
    echo "📦 Installing required system packages..."
    
    # Get Python version
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "3.12")
    echo "🔍 Detected Python ${PYTHON_VERSION}"
    
    # Install packages
    if command -v apt >/dev/null 2>&1; then
        echo "📥 Updating package list..."
        sudo apt update -qq
        
        echo "📦 Installing Python development packages..."
        # Try version-specific first, then generic
        if sudo apt install -y python${PYTHON_VERSION}-venv python3-venv python3-pip python3-full 2>/dev/null; then
            echo "✅ Version-specific packages installed"
        elif sudo apt install -y python3-venv python3-pip python3-full 2>/dev/null; then
            echo "✅ Generic packages installed"
        else
            echo "❌ Failed to install packages"
            return 1
        fi
    else
        echo "❌ apt not found - this script is designed for Debian/Ubuntu systems"
        return 1
    fi
}

# Check if sudo is available
if ! sudo -n true 2>/dev/null; then
    echo "⚠️  This script needs sudo access to install system packages."
    echo "Please run: sudo echo 'Testing sudo access' "
    echo "Then re-run this installer."
    exit 1
fi

# Install system dependencies
if ! install_deps; then
    echo "❌ Failed to install system dependencies"
    echo "Please try manually:"
    echo "  sudo apt update"
    echo "  sudo apt install python3-venv python3-pip python3-full"
    exit 1
fi

echo ""
echo "🗂️  Creating virtual environment..."

# Clean up any existing environment
if [ -d "optics-env" ]; then
    echo "🧹 Removing existing optics-env directory..."
    rm -rf optics-env
fi

# Create virtual environment
if python3 -m venv optics-env; then
    echo "✅ Virtual environment created"
else
    echo "❌ Failed to create virtual environment"
    echo "Please check the error above and try manual installation"
    exit 1
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source optics-env/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install the package
echo "📦 Installing optics-toolbox..."
pip install git+https://github.com/MichaelAkridge-NOAA/optics-toolbox.git

echo ""
echo "🎉 Installation complete!"
echo ""
echo "📋 To use optics-toolbox:"
echo "1. Activate the virtual environment:"
echo "   source optics-env/bin/activate"
echo ""
echo "2. Use the tools:"
echo "   gcs-browser browse gs://nmfs_odp_pifsc/"
echo "   gcs-browser-web"
echo ""
echo "3. For private buckets, authenticate first:"
echo "   gcloud auth login"
echo "   # or: gcloud init --no-launch-browser"
echo ""
echo "💡 Add this to your ~/.bashrc to make it easier:"
echo "   echo 'alias optics=\"source ~/optics-env/bin/activate\"' >> ~/.bashrc"
echo ""
echo "🎯 Quick start (run these commands):"
echo "   source optics-env/bin/activate"
echo "   gcs-browser browse gs://nmfs_odp_pifsc/"
