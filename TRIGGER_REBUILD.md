# 🚀 Trigger DigitalOcean Rebuild - PowerPro

## Option 1: Via DigitalOcean Dashboard (EASIEST)

1. Go to: https://cloud.digitalocean.com/apps
2. Click on **powerpro-automation**
3. Look for the **Activity** tab
4. You should see "New commit detected" 
5. If not, go to **Settings** → **Source**
6. Click **"Force Rebuild"** button
7. Watch the build progress in the Activity tab

## Option 2: Via doctl (if installed)

```bash
# 1. Install doctl if needed
brew install doctl

# 2. Set up your API token
echo "DO_API_TOKEN=your_actual_token_here" > .env.digitalocean
source .env.digitalocean

# 3. Authenticate
doctl auth init --access-token $DO_API_TOKEN

# 4. Get app ID
APP_ID=$(doctl apps list --format ID,Name --no-header | grep powerpro | awk '{print $1}')

# 5. Trigger deployment
doctl apps create-deployment $APP_ID --wait

# 6. Watch logs
doctl apps logs $APP_ID --follow
```

## What to Expect After Rebuild

### ✅ Success Signs:
- Build completes without errors
- Container shows as "Running"
- Logs show: "🎬 PowerPro TikTok Automation Starting"
- Logs show: "💚 Health: OK" every 30 seconds
- No "Exit Code" errors

### 📋 Expected Log Output:
```
2024-01-29 12:00:00 - INFO - ==================================================
2024-01-29 12:00:00 - INFO - 🎬 PowerPro TikTok Automation Starting
2024-01-29 12:00:00 - INFO - ==================================================
2024-01-29 12:00:01 - INFO - ✅ All directories created
2024-01-29 12:00:01 - INFO - ✅ All API keys configured
2024-01-29 12:00:01 - INFO - ⏸️ AUTO_PUBLISH=false - staying in health check mode
2024-01-29 12:00:01 - INFO - 🏥 Running in health check mode (container staying alive)
2024-01-29 12:00:01 - INFO - 📝 To start processing: Create /tmp/start_processing file
2024-01-29 12:00:31 - INFO - 💚 Health: OK | Time: 2024-01-29 12:00:31
2024-01-29 12:01:01 - INFO - 💚 Health: OK | Time: 2024-01-29 12:01:01
```

## Next Steps After Successful Deploy

1. **Container is now stable** - no more crashes!
2. **To enable processing**:
   - Go to Settings → Environment Variables
   - Change AUTO_PUBLISH from "false" to "true"
   - Save and redeploy
3. **Monitor initial processing**:
   - Watch logs for content discovery
   - Check for any API errors
   - Verify clips are being created

## Troubleshooting

### If build fails:
- Check build logs for specific error
- Most likely: requirements installation issue
- Solution: We have fallbacks in Dockerfile

### If container still exits:
- Check runtime logs
- Look for Python import errors
- The health check mode should prevent this

### If no "Health: OK" messages:
- Container may have crashed during startup
- Check for environment variable issues
- Verify start.py is being executed