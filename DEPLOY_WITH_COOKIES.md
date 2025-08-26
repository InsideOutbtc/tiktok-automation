# Complete Deployment Guide with YouTube Cookie Authentication

## Pre-Deployment: Cookie Setup (LOCAL)

**⚠️ MUST be done on your LOCAL computer, NOT the server!**

```bash
# 1. One-command setup
python scripts/setup_cookies.py

# Or manually:
python scripts/extract_cookies.py
python scripts/check_youtube_cookies.py
```

## Deployment to DigitalOcean

### Step 1: Prepare Files
```bash
# Ensure cookies exist
ls -la config/youtube_cookies.txt

# Create deployment package
tar -czf deploy.tar.gz \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='venv' \
  --exclude='.git' \
  --exclude='input/*' \
  --exclude='output/*' \
  .
```

### Step 2: Server Setup
```bash
# SSH to server
ssh root@your-server-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt-get install -y docker-compose

# Create app directory
mkdir -p /opt/fitness-tiktok
cd /opt/fitness-tiktok
```

### Step 3: Deploy Application
```bash
# On local machine - transfer files
scp deploy.tar.gz root@your-server-ip:/opt/fitness-tiktok/
scp config/youtube_cookies.txt root@your-server-ip:/opt/fitness-tiktok/config/

# On server - extract
cd /opt/fitness-tiktok
tar -xzf deploy.tar.gz
rm deploy.tar.gz

# Verify cookies
ls -la config/youtube_cookies.txt
```

### Step 4: Environment Configuration
```bash
# Create .env file
cat > .env << 'EOF'
YOUTUBE_API_KEY=your_youtube_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
YOUTUBE_COOKIE_FILE=/app/config/youtube_cookies.txt
AUTO_PUBLISH=false
ENVIRONMENT=production
EOF

# Set permissions
chmod 600 .env config/youtube_cookies.txt
```

### Step 5: Launch with Docker Compose
```bash
# Build and start
docker-compose up -d

# Verify it's running
docker-compose ps
docker-compose logs -f

# Test cookie validity inside container
docker-compose run --rm powerpro python scripts/check_youtube_cookies.py
```

## Verification Checklist

### 1. Cookie Validation
```bash
# Should see: "✅ COOKIES ARE WORKING!"
docker-compose run --rm powerpro python scripts/check_youtube_cookies.py
```

### 2. Dashboard Access
```bash
# Open in browser
http://your-server-ip:8000

# Test download with a YouTube URL
```

### 3. Check Logs
```bash
# Monitor for cookie-related messages
docker-compose logs -f | grep -i cookie

# Should see:
# "✓ Cookies found: /app/config/youtube_cookies.txt"
# "Using authenticated cookies from /app/config/youtube_cookies.txt"
```

## Monitoring & Maintenance

### Daily Checks
```bash
# Check download success rate
docker-compose exec powerpro python -c "
from src.core.youtube_downloader import ResilientYouTubeDownloader
d = ResilientYouTubeDownloader()
print(d.get_download_stats())
"
```

### Cookie Refresh (Monthly)
```bash
# On LOCAL machine
python scripts/setup_cookies.py

# Transfer to server
scp config/youtube_cookies.txt root@server:/opt/fitness-tiktok/config/

# Restart container
ssh root@server "cd /opt/fitness-tiktok && docker-compose restart"
```

## Troubleshooting

### "Sign in to confirm you're not a bot"
```bash
# Cookies are invalid/expired
# 1. Re-extract on local machine
python scripts/setup_cookies.py

# 2. Copy to server
scp config/youtube_cookies.txt root@server:/opt/fitness-tiktok/config/

# 3. Restart
docker-compose restart
```

### Downloads failing at 0%
```bash
# Check cookie file permissions
docker-compose exec powerpro ls -la /app/config/youtube_cookies.txt

# Should be readable by app user
docker-compose exec powerpro cat /app/config/youtube_cookies.txt | wc -l
# Should show 30+ lines
```

### No cookie file in container
```bash
# Ensure volume mount is correct
docker-compose down
docker-compose up -d

# Verify mount
docker-compose exec powerpro ls -la /app/config/
```

## Success Indicators

✅ Cookie validation passes
✅ Dashboard loads at :8000
✅ YouTube URLs download successfully
✅ Logs show "Downloaded via cookies"
✅ Success rate >90%

## Security Notes

1. **Never commit cookies to git**
2. **Rotate cookies monthly**
3. **Use read-only mount (:ro) in docker-compose**
4. **Monitor for unusual activity**

## Quick Commands Reference

```bash
# Setup cookies (local)
python scripts/setup_cookies.py

# Deploy to server
scp -r * root@server:/opt/fitness-tiktok/
ssh root@server "cd /opt/fitness-tiktok && docker-compose up -d"

# Check status
ssh root@server "cd /opt/fitness-tiktok && docker-compose ps"

# View logs
ssh root@server "cd /opt/fitness-tiktok && docker-compose logs -f"

# Refresh cookies
python scripts/setup_cookies.py
scp config/youtube_cookies.txt root@server:/opt/fitness-tiktok/config/
ssh root@server "cd /opt/fitness-tiktok && docker-compose restart"
```

Remember: **Without valid cookies, YouTube downloads WILL NOT WORK on cloud servers!**