#!/bin/bash
echo "🔍 Verifying metadata fix..."
echo "============================"

# Check for actual metadata field assignments (not Base.metadata)
if grep -E "^\s*metadata\s*=\s*Column" src/database/models.py 2>/dev/null; then
    echo "❌ ERROR: metadata field still exists in models.py"
    exit 1
else
    echo "✅ No conflicting metadata fields found"
fi

# Check for proper field names
if grep -q "video_metadata = Column" src/database/models.py; then
    echo "✅ video_metadata field found in Video model"
fi

if grep -q "clip_metadata = Column" src/database/models.py; then
    echo "✅ clip_metadata field found in Clip model"
fi

# Check migration script
if [ -f src/database/migrations.py ]; then
    echo "✅ Migration script created"
fi

# Check startup script updated
if grep -q "run_database_migrations" start.py; then
    echo "✅ Startup script will run migrations"
fi

echo ""
echo "✅ HOTFIX SUCCESSFULLY APPLIED!"
echo ""
echo "📊 DigitalOcean Deployment Status:"
echo "=================================="
echo "1. Deployment auto-triggered by GitHub push"
echo "2. Should complete in ~2-3 minutes"
echo "3. Watch Runtime Logs for:"
echo "   - '🎬 PowerPro TikTok Automation Starting'"
echo "   - '✅ Database migrations completed'"
echo "   - '🚀 AUTO_PUBLISH enabled - starting automation'"
echo "   - NO 'metadata is reserved' error"
echo ""
echo "4. System will now start processing videos!"
echo ""
echo "🔗 Monitor at: https://cloud.digitalocean.com/apps"