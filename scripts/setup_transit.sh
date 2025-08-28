#!/bin/bash
# setup_transit.sh - Proper macOS setup

echo "Setting up Video Transit System..."

# Get the actual path to the project
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT_PATH="$HOME/.video_transit/transit.py"
mkdir -p "$HOME/.video_transit"

# Copy the Python script to the transit directory
cp "$PROJECT_DIR/scripts/mac_transit_fixed.py" "$SCRIPT_PATH"
chmod +x "$SCRIPT_PATH"

# Create LaunchAgent (better than crontab on macOS)
PLIST="$HOME/Library/LaunchAgents/com.video.transit.plist"

cat > "$PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.video.transit</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$SCRIPT_PATH</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>10</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>$HOME/.video_transit/output.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.video_transit/error.log</string>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
</dict>
</plist>
EOF

# Unload if exists, then load
launchctl unload "$PLIST" 2>/dev/null
launchctl load "$PLIST"

echo "✅ Setup complete!"
echo ""
echo "Commands:"
echo "  Run now:        python3 $SCRIPT_PATH"
echo "  View logs:      tail -f $HOME/.video_transit.log"
echo "  Check status:   curl https://tiktok-automation-xqbnb.ondigitalocean.app/api/queue/status"
echo "  Reset queue:    curl -X POST https://tiktok-automation-xqbnb.ondigitalocean.app/api/queue/reset"
echo ""
echo "The system will run daily at 10 AM automatically."