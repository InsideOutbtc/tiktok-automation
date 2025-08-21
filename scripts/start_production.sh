#!/bin/bash

echo "🚀 TikTok AI Automation - Production Start"
echo "========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run: bash scripts/setup_system.sh"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Quick validation
echo "📍 Running quick validation..."
python3 scripts/quick_validate.py
if [ $? -ne 0 ]; then
    echo "❌ Validation failed. Please fix issues first."
    exit 1
fi

# Check for safe mode flag
SAFE_MODE=""
if [ "$1" = "--safe" ]; then
    SAFE_MODE="--safe"
    echo "🔒 Starting in SAFE MODE (no actual posting)"
else
    echo "⚠️  Starting in PRODUCTION MODE"
    echo "   Videos will be posted to TikTok!"
    echo "   Use --safe flag to run without posting"
    echo ""
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Cancelled."
        exit 0
    fi
fi

# Create log file
LOG_FILE="logs/production_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs

echo ""
echo "📊 Starting TikTok AI Automation..."
echo "   Log file: $LOG_FILE"
echo "   Press Ctrl+C to stop"
echo ""

# Start the main controller
python3 src/core/main_controller.py start $SAFE_MODE 2>&1 | tee "$LOG_FILE"

echo ""
echo "✅ System stopped"
echo "   Log saved to: $LOG_FILE"