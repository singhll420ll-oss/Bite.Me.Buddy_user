#!/usr/bin/env bash
# build.sh - Render build script

echo "Starting build process..."
echo "Python version: $(python --version)"

# Upgrade pip to latest version
pip install --upgrade pip

# Install Python dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p static/uploads

echo "Build completed successfully!"