#!/bin/bash

echo "🚀 TikTok AI - Quick Setup (No Homebrew updates)"
echo "=============================================="

# Skip Homebrew auto-update
export HOMEBREW_NO_AUTO_UPDATE=1

# 1. Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo "📍 Creating virtual environment..."
    python3 -m venv venv
fi

# 2. Activate virtual environment
source venv/bin/activate

# 3. Upgrade pip
echo "📍 Upgrading pip..."
python3 -m pip install --upgrade pip

# 4. Install Python dependencies
echo "📍 Installing Python dependencies..."
echo "  This may take a few minutes..."

# Install core dependencies first
pip install --no-cache-dir wheel setuptools

# Install all requirements
pip install --no-cache-dir -r requirements.txt

# 5. Create directories
echo "📍 Creating project directories..."
mkdir -p input/downloads
mkdir -p processing/{clips,temp,edited}
mkdir -p output
mkdir -p posted
mkdir -p logs
mkdir -p database
mkdir -p mcp-cache

# 6. Initialize database
echo "📍 Initializing database..."
python3 scripts/init_database.py

# 7. Quick validation
echo "📍 Running validation..."
python3 scripts/quick_validate.py

echo ""
echo "✅ Quick setup complete!"
echo ""
echo "⚠️  Note: FFmpeg still needs to be installed manually:"
echo "   macOS: brew install ffmpeg"
echo "   Linux: sudo apt-get install ffmpeg"
echo ""