#!/bin/bash
# setup_dynamic_transit.sh - Setup the transit system

echo "====================================="
echo "VIDEO TRANSIT SYSTEM SETUP"
echo "====================================="
echo ""

# Get DO URL
echo "Enter your DigitalOcean app URL:"
echo "Example: https://tiktok-automation-xqbnb.ondigitalocean.app"
read -r DO_URL

# Validate URL
if [[ ! "$DO_URL" =~ ^https://.*\.ondigitalocean\.app$ ]]; then
    echo "Warning: URL doesn't look like a DigitalOcean app URL"
    echo "Make sure it's correct!"
fi

# Create transit directory
TRANSIT_DIR="$HOME/.video_transit"
mkdir -p "$TRANSIT_DIR"

# Copy transit script
TRANSIT_SCRIPT="$TRANSIT_DIR/transit.py"
cp "$(dirname "$0")/mac_transit.py" "$TRANSIT_SCRIPT"

# Replace placeholder with actual URL
sed -i '' "s|https://\[YOUR-APP-NAME\]\.ondigitalocean\.app|$DO_URL|g" "$TRANSIT_SCRIPT"

chmod +x "$TRANSIT_SCRIPT"

# Create LaunchAgent for daily runs
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
        <string>$TRANSIT_SCRIPT</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>10</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>EnvironmentVariables</key>
    <dict>
        <key>DO_URL</key>
        <string>$DO_URL</string>
    </dict>
    <key>StandardOutPath</key>
    <string>$TRANSIT_DIR/output.log</string>
    <key>StandardErrorPath</key>
    <string>$TRANSIT_DIR/error.log</string>
</dict>
</plist>
EOF

# Unload and reload
launchctl unload "$PLIST" 2>/dev/null
launchctl load "$PLIST"

echo ""
echo "✅ Setup complete!"
echo ""
echo "COMMANDS:"
echo "  Test now:       python3 $TRANSIT_SCRIPT"
echo "  View logs:      tail -f $HOME/.video_transit.log"
echo "  Check queue:    curl $DO_URL/api/queue | python3 -m json.tool"
echo "  Queue status:   curl $DO_URL/api/queue/status | python3 -m json.tool"
echo "  Reset queue:    curl -X POST $DO_URL/api/queue/reset"
echo ""
echo "The system will run automatically every day at 10:00 AM"
echo ""

# Ask if they want to test now
echo "Would you like to test the system now? (y/n)"
read -r TEST_NOW

if [[ "$TEST_NOW" =~ ^[Yy]$ ]]; then
    echo ""
    echo "Testing the transit system..."
    python3 "$TRANSIT_SCRIPT"
fi