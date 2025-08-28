#!/bin/bash
# Monitor clip generation progress

echo "📊 MONITORING CLIP GENERATION"
echo "============================"
echo "Press Ctrl+C to stop monitoring"
echo ""

DO_URL="https://powerpro-automation-f2k4p.ondigitalocean.app"

while true; do
    echo -n "$(date '+%H:%M:%S') - "
    
    # Get clip count
    CLIPS=$(curl -s "$DO_URL/api/clips" | python3 -c "import json,sys; data=json.load(sys.stdin); print(len(data.get('clips',[])))")
    
    if [ "$CLIPS" = "0" ]; then
        echo "⏳ No clips yet... (processing)"
    else
        echo "✅ $CLIPS clips generated!"
        echo ""
        echo "🎉 Clips are ready!"
        echo "🌐 View them at: $DO_URL/dashboard"
        break
    fi
    
    sleep 10
done