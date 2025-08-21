#!/bin/bash

echo "🔍 Verifying PowerPro Deployment"
echo "================================"

# If doctl is available
if command -v doctl &> /dev/null; then
    APP_ID=$(doctl apps list --format "ID,Name" --no-header | grep "powerpro-automation" | awk '{print $1}')
    
    if [ -n "$APP_ID" ]; then
        echo "📱 Checking app status..."
        
        # Get app status
        STATUS=$(doctl apps get $APP_ID --format "ActiveDeployment.Phase" --no-header)
        
        if [ "$STATUS" = "ACTIVE" ]; then
            echo "✅ Deployment SUCCESSFUL!"
            echo ""
            echo "📋 Getting recent logs..."
            doctl apps logs $APP_ID --type=run --tail=20
        else
            echo "⏳ Deployment status: $STATUS"
            echo "Please wait for deployment to complete..."
        fi
    fi
else
    echo "📝 Manual verification steps:"
    echo "1. Go to: https://cloud.digitalocean.com/apps"
    echo "2. Click on 'powerpro-automation'"
    echo "3. Check Activity tab - should show 'Deployed'"
    echo "4. Check Runtime Logs - should show health checks"
    echo ""
    echo "Expected logs:"
    echo "  - 'PowerPro TikTok Automation Starting'"
    echo "  - 'Health: OK' messages every 30 seconds"
    echo "  - 'AUTO_PUBLISH=false - staying in health check mode'"
fi

echo ""
echo "🎯 Next Steps:"
echo "1. Container should be running (no exit errors)"
echo "2. To enable processing: Set AUTO_PUBLISH=true in DigitalOcean"
echo "3. Monitor logs for health checks"