#!/bin/bash
# Quick install script for cloud workstations
# Usage: curl -sSL https://raw.githubusercontent.com/MichaelAkridge-NOAA/optics-toolbox/main/install-cloud.sh | bash

set -e

echo "🌩️ Installing Optics Toolbox for Cloud Workstation..."

# Function to check if we're in an externally managed environment
check_managed_env() {
    # Try a test pip install to see if we get the externally-managed error
    pip install --dry-run setuptools 2>&1 | grep -q "externally-managed-environment" || 
    python3 -c "import sys; print('externally-managed' if hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix else 'ok')" 2>/dev/null | grep -q "ok" &&
    pip install --help 2>/dev/null | grep -q "break-system-packages"
}

# Function to install system packages if needed
install_system_deps() {
    echo "📦 Installing required system packages..."
    
    # Check if we have sudo access
    if sudo -n true 2>/dev/null; then
        # Try to install python3-venv and python3-pip
        if command -v apt >/dev/null 2>&1; then
            sudo apt update -qq
            sudo apt install -y python3-venv python3-pip python3-full 2>/dev/null || true
        elif command -v yum >/dev/null 2>&1; then
            sudo yum install -y python3-venv python3-pip 2>/dev/null || true
        fi
    else
        echo "⚠️  No sudo access. You may need to install python3-venv manually:"
        echo "   sudo apt install python3-venv python3-full"
    fi
}

# Check if we're in a managed environment by attempting a test install
MANAGED_ENV=false
if check_managed_env; then
    MANAGED_ENV=true
    echo "📦 Detected externally-managed environment"
else
    echo "📦 Standard environment detected"
fi

# If managed environment, use virtual environment
if [ "$MANAGED_ENV" = true ]; then
    echo "🔧 Using virtual environment approach..."
    
    # Ensure system dependencies are available
    if ! python3 -m venv --help >/dev/null 2>&1; then
        echo "⚠️  python3-venv not available, attempting to install..."
        install_system_deps
    fi
    
    # Create virtual environment
    echo "📂 Creating virtual environment..."
    if python3 -m venv optics-env 2>/dev/null; then
        source optics-env/bin/activate
        echo "✅ Virtual environment created and activated"
        echo "💡 To use later, run: source optics-env/bin/activate"
    else
        echo "❌ Failed to create virtual environment."
        echo "� Trying alternative: pipx install..."
        
        # Try pipx as fallback
        if command -v pipx >/dev/null 2>&1; then
            pipx install git+https://github.com/MichaelAkridge-NOAA/optics-toolbox.git
            echo "✅ Installed with pipx - commands available system-wide"
            exit 0
        else
            echo "⚠️  pipx not available. Manual installation required:"
            echo ""
            echo "Option 1 - Install system packages:"
            echo "  sudo apt update && sudo apt install python3-venv python3-full"
            echo "  python3 -m venv optics-env && source optics-env/bin/activate"
            echo "  pip install git+https://github.com/MichaelAkridge-NOAA/optics-toolbox.git"
            echo ""
            echo "Option 2 - Use pipx:"
            echo "  sudo apt install pipx"
            echo "  pipx install git+https://github.com/MichaelAkridge-NOAA/optics-toolbox.git"
            echo ""
            echo "Option 3 - System override (not recommended):"
            echo "  pip install git+https://github.com/MichaelAkridge-NOAA/optics-toolbox.git --break-system-packages"
            exit 1
        fi
    fi
fi

# Install the package
echo "⬬ Installing optics-toolbox..."
pip install git+https://github.com/MichaelAkridge-NOAA/optics-toolbox.git

echo ""
echo "🎉 Installation complete!"
echo ""
echo "🚀 Quick start:"
if [ "$MANAGED_ENV" = true ]; then
    echo "   source optics-env/bin/activate  # (activate virtual environment first)"
fi
echo "   gcs-browser browse gs://nmfs_odp_pifsc/"
echo "   gcs-browser-web"
echo ""
echo "🔧 For private buckets, authenticate first:"
echo "   gcloud auth login"
echo "   # or: gcloud init --no-launch-browser"
