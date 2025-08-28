#!/bin/bash
# Setup script for Daily Batch Processor

echo "🎬 Setting up Daily Batch Processor"
echo "===================================="

# Create necessary directories
mkdir -p ~/Patrick/Fitness\ TikTok/downloads
mkdir -p ~/Patrick/Fitness\ TikTok/clips
mkdir -p ~/Patrick/Fitness\ TikTok/approved
mkdir -p ~/Patrick/Fitness\ TikTok/logs

# Install required packages if not present
echo "Checking dependencies..."
if ! command -v yt-dlp &> /dev/null; then
    echo "Installing yt-dlp..."
    brew install yt-dlp || pip3 install yt-dlp
fi

# Create LaunchAgent for daily execution (9 AM daily)
PLIST_FILE=~/Library/LaunchAgents/com.powerpro.dailybatch.plist

cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.powerpro.dailybatch</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$HOME/Patrick/Fitness TikTok/scripts/daily_batch_processor.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>$HOME/Patrick/Fitness TikTok/logs/daily_batch.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Patrick/Fitness TikTok/logs/daily_batch_error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
EOF

# Load the LaunchAgent
echo "Loading LaunchAgent..."
launchctl unload "$PLIST_FILE" 2>/dev/null
launchctl load "$PLIST_FILE"

echo "✅ Daily Batch Processor installed!"
echo ""
echo "It will run automatically every day at 9 AM"
echo ""
echo "To run manually now:"
echo "python3 ~/Patrick/Fitness\ TikTok/scripts/daily_batch_processor.py"
echo ""
echo "To view the review dashboard:"
echo "python3 ~/Patrick/Fitness\ TikTok/scripts/content_review_dashboard.py"
echo "Then open: http://localhost:5000"