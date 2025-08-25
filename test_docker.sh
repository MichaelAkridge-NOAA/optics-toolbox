#!/bin/bash

# Quick Docker test for debugging the web app
echo "🧪 Building test Docker image..."

# Build test image
docker build -f Dockerfile.test -t optics-toolbox-test .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo "✅ Build successful!"
echo ""
echo "🚀 Starting test container..."
echo "📱 Access the test app at: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Run container with port forwarding
docker run --rm -p 8501:8501 optics-toolbox-test
