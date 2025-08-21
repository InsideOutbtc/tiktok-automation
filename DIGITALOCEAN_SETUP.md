# DigitalOcean Deployment Setup Guide

## Step 1: Install DigitalOcean CLI (doctl)

### On macOS:
```bash
brew install doctl
```

### Alternative (if brew not available):
```bash
# Download the latest release
curl -sL https://github.com/digitalocean/doctl/releases/download/v1.104.0/doctl-1.104.0-darwin-amd64.tar.gz | tar -xzv
# Move to PATH
sudo mv doctl /usr/local/bin
```

## Step 2: Create API Token

1. Go to https://cloud.digitalocean.com/account/api/tokens
2. Click "Generate New Token"
3. Name it "powerpro-deployment"
4. Give it Read and Write access
5. Copy the token (you won't see it again!)

## Step 3: Save Token Securely

Create `.env.digitalocean` file:
```bash
echo "DO_API_TOKEN=your_token_here" > .env.digitalocean
```

## Step 4: Authenticate doctl

```bash
# Load token
source .env.digitalocean

# Authenticate
doctl auth init --access-token $DO_API_TOKEN

# Verify
doctl account get
```

## Step 5: Deploy App

```bash
# Make sure you're in the project directory
cd ~/Patrick/Fitness\ TikTok

# Push to GitHub first
git add -A
git commit -m "Fix deployment: imports and dockerfile"
git push origin main

# Create the app
doctl apps create --spec app.yaml

# Or if app exists, update it
APP_ID=$(doctl apps list --format ID,Name --no-header | grep powerpro | awk '{print $1}')
doctl apps update $APP_ID --spec app.yaml
```

## Step 6: Add Environment Variables

After app creation, add your API keys in the DigitalOcean dashboard:
1. Go to https://cloud.digitalocean.com/apps
2. Click on your app
3. Go to Settings → Environment Variables
4. Add:
   - YOUTUBE_API_KEY = your_youtube_key
   - OPENAI_API_KEY = your_openai_key

## Step 7: Monitor Deployment

```bash
# Get app ID
APP_ID=$(doctl apps list --format ID --no-header | grep powerpro | head -1)

# Watch logs
doctl apps logs $APP_ID --follow

# Check status
doctl apps get $APP_ID
```

## Quick Deployment Script

Save this as `deploy.sh`:
```bash
#!/bin/bash
source .env.digitalocean

echo "🚀 Deploying PowerPro to DigitalOcean..."

# Push to GitHub
git add -A
git commit -m "Deploy update"
git push origin main

# Get app ID
APP_ID=$(doctl apps list --format ID,Name --no-header | grep powerpro | awk '{print $1}')

if [ -z "$APP_ID" ]; then
    echo "Creating new app..."
    doctl apps create --spec app.yaml --wait
else
    echo "Updating existing app..."
    doctl apps update $APP_ID --spec app.yaml --wait
fi

echo "✅ Deployment complete!"
```

## Troubleshooting

### If deployment fails:
1. Check logs: `doctl apps logs $APP_ID --type build`
2. Verify GitHub connection
3. Check environment variables
4. Ensure requirements.txt is valid

### Common issues:
- **Import errors**: Already fixed with absolute imports
- **Missing modules**: Using requirements_essential.txt as fallback
- **Path issues**: PYTHONPATH set in Dockerfile