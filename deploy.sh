#!/bin/bash
# PowerPro DigitalOcean Deployment Script

echo "🚀 PowerPro Deployment Script"
echo "============================"

# Check for environment file
if [ ! -f .env.digitalocean ]; then
    echo "❌ Missing .env.digitalocean file"
    echo "Please create it with: DO_API_TOKEN=your_token_here"
    exit 1
fi

# Load environment
source .env.digitalocean

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "❌ doctl is not installed"
    echo "Install with: brew install doctl"
    echo "Or see DIGITALOCEAN_SETUP.md for instructions"
    exit 1
fi

# Authenticate doctl
echo "🔐 Authenticating with DigitalOcean..."
doctl auth init --access-token $DO_API_TOKEN 2>/dev/null || {
    echo "❌ Authentication failed. Check your DO_API_TOKEN"
    exit 1
}

# Verify authentication
doctl account get > /dev/null 2>&1 || {
    echo "❌ Cannot access DigitalOcean account"
    exit 1
}

echo "✅ Authenticated successfully"

# Commit and push changes
echo "📦 Preparing code for deployment..."
git add -A
git commit -m "Deploy PowerPro automation" || echo "No changes to commit"
git push origin main || {
    echo "❌ Failed to push to GitHub"
    echo "Make sure you have set up the remote: git remote add origin https://github.com/InsideOutbtc/tiktok-automation.git"
    exit 1
}

echo "✅ Code pushed to GitHub"

# Check if app already exists
APP_ID=$(doctl apps list --format ID,Name --no-header | grep "powerpro-automation" | awk '{print $1}')

if [ -z "$APP_ID" ]; then
    echo "📱 Creating new app..."
    APP_ID=$(doctl apps create --spec app.yaml --format ID --no-header)
    
    if [ -z "$APP_ID" ]; then
        echo "❌ Failed to create app"
        exit 1
    fi
    
    echo "✅ App created with ID: $APP_ID"
    echo ""
    echo "⚠️  IMPORTANT: Add your API keys in DigitalOcean dashboard:"
    echo "   1. Go to https://cloud.digitalocean.com/apps/$APP_ID/settings"
    echo "   2. Click on Environment Variables"
    echo "   3. Add YOUTUBE_API_KEY and OPENAI_API_KEY"
    echo ""
else
    echo "📱 Updating existing app (ID: $APP_ID)..."
    doctl apps update $APP_ID --spec app.yaml
    echo "✅ App updated"
fi

# Get app URL
echo ""
echo "🌐 Getting app information..."
APP_URL=$(doctl apps get $APP_ID --format DefaultIngress --no-header)

echo ""
echo "📊 Deployment Status:"
echo "===================="
doctl apps get $APP_ID --format Status,DefaultIngress,UpdatedAt --no-header

echo ""
echo "📋 Useful commands:"
echo "===================="
echo "View logs:        doctl apps logs $APP_ID --follow"
echo "Check status:     doctl apps get $APP_ID"
echo "View in browser:  https://cloud.digitalocean.com/apps/$APP_ID"

echo ""
echo "🎉 Deployment complete!"