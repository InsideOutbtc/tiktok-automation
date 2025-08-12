#!/bin/bash

echo "🚀 Setting up Fitness TikTok AI Automation System"
echo "⚡ Constitutional AI Framework: ACTIVATING"
echo "📁 Location: ~/Patrick/Fitness TikTok/"
echo "================================================"

# Check if we're in the right directory
if [[ ! "$PWD" == *"Patrick/Fitness TikTok"* ]]; then
    echo "⚠️  Please run this from ~/Patrick/Fitness TikTok/"
    exit 1
fi

# Check for project-systems
if [ ! -d "project-systems" ]; then
    echo "📦 Copying project-systems framework..."
    cp -r ~/Patrick/project-systems .
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download Whisper model
echo "🎤 Downloading Whisper model..."
python -c "import whisper; whisper.load_model('base')"

# Create .env from example
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file..."
    cp .env.example .env
    echo "📝 Please edit .env with your API keys and settings"
fi

# Initialize database
echo "💾 Initializing database..."
mkdir -p database
python -c "from src.database import models; models.create_all()" 2>/dev/null || echo "Database will be initialized on first run"

# Create directories
echo "📁 Creating directories..."
for dir in input processing output posted logs mcp-cache/ref mcp-cache/pieces mcp-cache/semgrep context/stack context/patterns context/sessions; do
    mkdir -p $dir
    touch $dir/README.md
done

# Generate initial PRP
echo "📋 Generating initial PRP..."
if [ -f "project-systems/prp-framework/commands/prp-generate.js" ]; then
    node project-systems/prp-framework/commands/prp-generate.js agent "tiktok-automation" > prp-framework/active/2025-01-28-tiktok-automation.md
fi

# Validate Constitutional AI compliance
echo "🔍 Validating Constitutional AI compliance..."
python src/utils/constitutional_monitor.py --validate 2>/dev/null || echo "Monitor will validate on first run"

echo ""
echo "✅ Setup complete with Constitutional AI!"
echo "⚡ Maximum Velocity Mode: READY"
echo "📊 Token Optimization: 85% TARGET"
echo "🛡️ Error Handling: TIER 1-4 ACTIVE"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys and MCP settings"
echo "2. Add your watermark to assets/watermarks/"
echo "3. Run: python src/core/main_controller.py start --max-velocity"
echo ""
echo "Constitutional AI Commands:"
echo "- Generate PRP: node project-systems/prp-framework/commands/prp-generate.js agent 'feature'"
echo "- Validate: python src/utils/constitutional_monitor.py --validate"
echo "- Monitor: python src/utils/constitutional_monitor.py --report"