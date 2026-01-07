#!/bin/bash
# start.sh - Start script for Render

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Create uploads directory
mkdir -p static/uploads

# Run the application with gunicorn
gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120