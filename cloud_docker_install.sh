#!/bin/bash
# Docker-based install script for cloud environments
# Usage: curl -sSL https://raw.githubusercontent.com/MichaelAkridge-NOAA/optics-toolbox/main/cloud_docker_install.sh | bash

set -e

echo "🐳 Docker-based Optics Toolbox Installation"
echo "============================================"

# Function to check if docker is available
check_docker() {
    if ! command -v docker >/dev/null 2>&1; then
        echo "❌ Docker not found. Installing Docker..."
        
        if command -v apt >/dev/null 2>&1; then
            # Install Docker on Ubuntu/Debian
            sudo apt update -qq
            sudo apt install -y docker.io docker-compose
            sudo systemctl start docker
            sudo systemctl enable docker
            
            # Add user to docker group
            sudo usermod -aG docker $USER
            echo "⚠️  You may need to log out and back in for Docker group changes to take effect"
            echo "   Or run: newgrp docker"
        else
            echo "❌ Cannot install Docker automatically on this system"
            echo "Please install Docker manually and re-run this script"
            exit 1
        fi
    else
        echo "✅ Docker found"
    fi
}

# Function to test docker access
test_docker() {
    if ! docker ps >/dev/null 2>&1; then
        echo "⚠️  Docker daemon not accessible. Trying to fix..."
        
        # Try to start docker service
        sudo systemctl start docker 2>/dev/null || true
        
        # Try newgrp docker
        if groups | grep -q docker; then
            echo "✅ User is in docker group"
        else
            echo "⚠️  Adding user to docker group..."
            sudo usermod -aG docker $USER
            echo "Please run: newgrp docker"
            echo "Then re-run this script"
            exit 1
        fi
        
        # Test again
        if ! docker ps >/dev/null 2>&1; then
            echo "❌ Still cannot access Docker. Please run:"
            echo "   sudo systemctl start docker"
            echo "   newgrp docker"
            echo "Then re-run this script"
            exit 1
        fi
    fi
    echo "✅ Docker is accessible"
}

# Create directory structure
setup_directories() {
    echo "📁 Setting up directories..."
    
    # Create main directory
    mkdir -p ~/optics-toolbox
    cd ~/optics-toolbox
    
    # Create data directories
    mkdir -p data/downloads
    mkdir -p data/credentials
    mkdir -p logs
    
    echo "✅ Directories created in ~/optics-toolbox"
}

# Create Dockerfile
create_dockerfile() {
    echo "🐳 Creating Dockerfile..."
    
    cat > Dockerfile << 'EOF'
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1000 appuser
USER appuser
WORKDIR /home/appuser

# Install optics-toolbox
RUN pip install --user git+https://github.com/MichaelAkridge-NOAA/optics-toolbox.git

# Add user's pip bin to PATH
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Create directories
RUN mkdir -p /home/appuser/data/downloads /home/appuser/data/credentials

# Expose Streamlit port
EXPOSE 8501

# Default command
CMD ["gcs-browser-web", "--server.address=0.0.0.0", "--server.port=8501"]
EOF

    echo "✅ Dockerfile created"
}

# Create docker-compose.yml
create_compose() {
    echo "📝 Creating docker-compose.yml..."
    
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  optics-toolbox:
    build: .
    container_name: optics-toolbox
    ports:
      - "8501:8501"
    volumes:
      - ./data/downloads:/home/appuser/data/downloads
      - ./data/credentials:/home/appuser/data/credentials
      - ./logs:/home/appuser/logs
    environment:
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
    restart: unless-stopped
    
  # Optional: CLI service for running commands
  optics-cli:
    build: .
    container_name: optics-cli
    volumes:
      - ./data/downloads:/home/appuser/data/downloads
      - ./data/credentials:/home/appuser/data/credentials
    profiles: ["cli"]
    command: tail -f /dev/null  # Keep container running
EOF

    echo "✅ docker-compose.yml created"
}

# Create helper scripts
create_scripts() {
    echo "📜 Creating helper scripts..."
    
    # Web interface script
    cat > start-web.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Optics Toolbox Web Interface..."
docker-compose up -d optics-toolbox

echo ""
echo "✅ Web interface started!"
echo "🌐 Access at: http://localhost:8501"
echo "📁 Downloads will be saved to: $(pwd)/data/downloads"
echo ""
echo "🔧 To stop: docker-compose down"
echo "📊 To view logs: docker-compose logs -f optics-toolbox"
EOF

    # CLI script  
    cat > optics-cli.sh << 'EOF'
#!/bin/bash
# Run optics-toolbox CLI commands in Docker

if [ $# -eq 0 ]; then
    echo "Usage: ./optics-cli.sh <command>"
    echo ""
    echo "Examples:"
    echo "  ./optics-cli.sh gcs-browser browse gs://nmfs_odp_pifsc/"
    echo "  ./optics-cli.sh gcs-browser download gs://bucket/file.txt ./data/downloads/"
    echo ""
    echo "Or start interactive shell:"
    echo "  ./optics-cli.sh bash"
    exit 1
fi

# Start CLI container if not running
docker-compose --profile cli up -d optics-cli >/dev/null 2>&1

# Execute command
docker-compose exec optics-cli "$@"
EOF

    # Stop script
    cat > stop.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping Optics Toolbox..."
docker-compose down
echo "✅ Stopped"
EOF

    # Make scripts executable
    chmod +x start-web.sh optics-cli.sh stop.sh
    
    echo "✅ Helper scripts created"
}

# Create usage instructions
create_readme() {
    echo "📖 Creating usage instructions..."
    
    cat > README.md << 'EOF'
# Optics Toolbox Docker Installation

## Quick Start

### Web Interface
```bash
./start-web.sh
# Open browser to http://localhost:8501
```

### Command Line
```bash
# Browse a bucket
./optics-cli.sh gcs-browser browse gs://nmfs_odp_pifsc/

# Download files
./optics-cli.sh gcs-browser download gs://bucket/file.txt ./data/downloads/

# Interactive shell
./optics-cli.sh bash
```

## File Locations
- **Downloads**: `./data/downloads/`
- **Credentials**: `./data/credentials/` (place your service account keys here)
- **Logs**: `./logs/`

## Management
```bash
# Start web interface
./start-web.sh

# Stop everything
./stop.sh

# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Update to latest version
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Authentication
1. For service account: Place JSON key in `./data/credentials/`
2. For gcloud auth: Run `./optics-cli.sh gcloud auth login`

## Troubleshooting
- Check logs: `docker-compose logs optics-toolbox`
- Restart: `docker-compose restart`
- Rebuild: `docker-compose build --no-cache`
EOF

    echo "✅ README.md created"
}

# Main installation process
main() {
    echo "Starting Docker-based installation..."
    echo ""
    
    check_docker
    test_docker
    setup_directories
    create_dockerfile
    create_compose
    create_scripts
    create_readme
    
    echo ""
    echo "🎉 Installation Complete!"
    echo "=============================="
    echo ""
    echo "📁 Installation directory: ~/optics-toolbox"
    echo "🌐 To start web interface: cd ~/optics-toolbox && ./start-web.sh"
    echo "⚡ To use CLI: cd ~/optics-toolbox && ./optics-cli.sh gcs-browser browse gs://nmfs_odp_pifsc/"
    echo ""
    echo "🚀 Quick start:"
    echo "   cd ~/optics-toolbox"
    echo "   ./start-web.sh"
    echo "   # Open browser to http://localhost:8501"
    echo ""
    echo "📖 See README.md for full instructions"
}

# Run main function
main
