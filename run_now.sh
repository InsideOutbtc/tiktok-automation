#!/bin/bash
# No-dependency pipeline runner - uses only system commands

echo "🚀 INSTANT PIPELINE RUNNER"
echo "========================="

DO_URL="https://powerpro-automation-f2k4p.ondigitalocean.app"
COOKIE_FILE="/Users/Patrick/Fitness TikTok/config/youtube_cookies.txt"

# Test video (short fitness clip)
TEST_VIDEO="https://www.youtube.com/watch?v=ScMzIvxBSi4"
OUTPUT="/tmp/test_fitness.mp4"

echo "📡 Checking DO app..."
if curl -s -f "${DO_URL}/health" > /dev/null; then
    echo "✅ DO app is healthy"
else
    echo "⚠️ DO app may be down, continuing anyway..."
fi

echo ""
echo "🎬 Downloading test video..."
echo "   URL: $TEST_VIDEO"

# Try yt-dlp first (if available from brew install)
if command -v yt-dlp &> /dev/null; then
    echo "✅ Using yt-dlp"
    yt-dlp --cookies "$COOKIE_FILE" \
           -f "best[height<=720]" \
           --max-filesize 100M \
           -o "$OUTPUT" \
           "$TEST_VIDEO" 2>/dev/null
else
    echo "❌ yt-dlp not found"
    echo "   Install with: brew install yt-dlp"
    echo "   Or: pip3 install yt-dlp"
fi

# Check if download succeeded
if [ -f "$OUTPUT" ]; then
    SIZE=$(du -h "$OUTPUT" | cut -f1)
    echo "✅ Downloaded: $SIZE"
    
    echo ""
    echo "⬆️ Uploading to DigitalOcean..."
    
    # Upload with curl
    RESPONSE=$(curl -X POST "${DO_URL}/api/upload" \
                    -F "video=@${OUTPUT}" \
                    -F "video_id=test_$(date +%s)" \
                    -w "\nHTTP_CODE:%{http_code}" \
                    -s)
    
    HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ Upload successful!"
    else
        echo "❌ Upload failed (HTTP $HTTP_CODE)"
        echo "Response: $(echo "$RESPONSE" | head -5)"
    fi
    
    # Cleanup
    rm -f "$OUTPUT"
    echo "🗑️ Cleaned up temp file"
else
    echo "❌ Download failed"
    echo ""
    echo "📝 Manual steps to try:"
    echo "1. Install yt-dlp: brew install yt-dlp"
    echo "2. Run this script again: ./run_now.sh"
fi

echo ""
echo "======================================"
echo "✅ PIPELINE RUN COMPLETE"
echo ""
echo "🌐 Dashboard: ${DO_URL}/dashboard"
echo "⏰ Check in 5-10 minutes for clips"
echo ""
echo "💡 Next steps:"
echo "   - Visit dashboard to see processing status"
echo "   - Download generated clips"
echo "   - Upload to TikTok"
echo "======================================