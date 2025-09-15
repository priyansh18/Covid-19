#!/bin/bash
set -e  # Exit on error

echo "🚀 Starting build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
python3.9 -m pip install --upgrade pip
python3.9 -m pip install -r requirements.txt

# Collect static files
echo "🛠️  Collecting static files..."
python3.9 manage.py collectstatic --noinput --clear

echo "✅ Build completed successfully!"
