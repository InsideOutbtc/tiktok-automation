#!/bin/bash
echo "🚀 Starting PowerPro TikTok Automation"

# Check environment
if [ ! -f .env ]; then
    echo "❌ .env file not found. Copy .env.example and configure."
    exit 1
fi

# Check Python
python --version || python3 --version

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run migrations
echo "📊 Running database migrations..."
python src/database/migrations.py

# Process logos if not done
if [ ! -f "assets/logos/profile_200x200.png" ]; then
    echo "🎨 Processing logos..."
    python scripts/process_logos.py
fi

# Start the system
echo "✅ Starting automation system..."
python src/core/main_controller.py start --max-velocity