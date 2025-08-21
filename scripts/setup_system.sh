#!/bin/bash

echo "🚀 TikTok AI Automation - Complete Setup"
echo "========================================"
echo "This script will install all dependencies and prepare your system"
echo ""

# Check OS
OS="$(uname)"
if [ "$OS" != "Darwin" ]; then
    echo "⚠️  Warning: This script is optimized for macOS"
    echo "    Linux users may need to adjust commands"
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Check Python 3
echo "📍 Checking Python 3..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "  ✅ Python $PYTHON_VERSION found"
else
    echo "  ❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# 2. Check/Install Homebrew (macOS)
if [ "$OS" = "Darwin" ]; then
    echo "📍 Checking Homebrew..."
    if ! command_exists brew; then
        echo "  ⚠️  Homebrew not found. Installing..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        echo "  ✅ Homebrew installed"
    fi
fi

# 3. Install FFmpeg
echo "📍 Checking FFmpeg..."
if ! command_exists ffmpeg; then
    echo "  ⚠️  FFmpeg not found. Installing..."
    if [ "$OS" = "Darwin" ]; then
        brew install ffmpeg
    else
        sudo apt-get update && sudo apt-get install -y ffmpeg
    fi
else
    echo "  ✅ FFmpeg installed"
fi

# 4. Upgrade pip
echo "📍 Upgrading pip..."
python3 -m pip install --upgrade pip

# 5. Install Python dependencies
echo "📍 Installing Python dependencies..."
echo "  This may take a few minutes..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install core dependencies first
pip install --no-cache-dir wheel setuptools

# Install all requirements
pip install --no-cache-dir -r requirements.txt

# 6. Install Playwright browsers
echo "📍 Installing Playwright browsers..."
python3 -m playwright install chromium

# 7. Download Whisper model (optional for video analysis)
echo "📍 Downloading AI models..."
python3 -c "
try:
    import whisper
    print('  Downloading Whisper base model...')
    whisper.load_model('base')
    print('  ✅ Whisper model ready')
except:
    print('  ⚠️  Whisper not available (optional)')
"

# 8. Create necessary directories
echo "📍 Creating project directories..."
mkdir -p input/downloads
mkdir -p processing/{clips,temp,edited}
mkdir -p output
mkdir -p posted
mkdir -p logs
mkdir -p database
mkdir -p mcp-cache

echo "  ✅ All directories created"

# 9. Initialize database
echo "📍 Initializing database..."
python3 -c "
import sqlite3
import os

db_path = 'database/tiktok_automation.db'
os.makedirs('database', exist_ok=True)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    video_id TEXT UNIQUE NOT NULL,
    title TEXT,
    url TEXT,
    views INTEGER,
    likes INTEGER,
    engagement_score REAL,
    download_status TEXT DEFAULT 'pending',
    local_path TEXT,
    processed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS clips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER,
    clip_number INTEGER,
    start_time REAL,
    end_time REAL,
    duration REAL,
    score REAL,
    title TEXT,
    description TEXT,
    hashtags TEXT,
    posted BOOLEAN DEFAULT 0,
    post_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(id)
)
''')

# Create indexes for performance
cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_processed ON videos(processed)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_clips_score ON clips(score DESC)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_clips_posted ON clips(posted)')

conn.commit()
conn.close()

print('  ✅ Database initialized')
"

# 10. Verify .env file
echo "📍 Checking configuration..."
if [ -f ".env" ]; then
    echo "  ✅ .env file found"
    
    # Check for API keys (without showing them)
    if grep -q "YOUTUBE_API_KEY=AIza" .env && grep -q "OPENAI_API_KEY=sk-" .env; then
        echo "  ✅ API keys appear to be configured"
    else
        echo "  ⚠️  Warning: API keys may not be properly configured"
        echo "     Please verify your .env file has valid keys"
    fi
else
    echo "  ⚠️  .env file not found!"
    echo "     Creating from template..."
    cp .env.example .env
    echo "     ⚠️  Please edit .env and add your API keys"
fi

echo ""
echo "========================================"
echo "✅ SETUP COMPLETE!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Ensure your API keys are in .env file"
echo "2. Run tests: python3 scripts/test_apis.py"
echo "3. Start system: python3 src/core/main_controller.py start"
echo ""
echo "Virtual environment activated. To deactivate: deactivate"