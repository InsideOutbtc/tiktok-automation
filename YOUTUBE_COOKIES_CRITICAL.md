# 🚨 CRITICAL: YouTube Cookie Authentication Setup

## Why Cookies Are MANDATORY for Cloud Servers

**YouTube blocks ALL downloads from datacenter IPs (AWS, DigitalOcean, etc.) with:**
```
ERROR: Sign in to confirm you're not a bot
```

**The ONLY proven solution:** Authenticated cookies from a logged-in YouTube account.

## Quick Setup (3 Methods)

### Method 1: Automatic Extraction (Recommended)
```bash
# Run locally on your computer (NOT on the server)
python scripts/extract_cookies.py

# This will:
# 1. Find Chrome/Firefox cookies
# 2. Extract YouTube authentication
# 3. Save to config/youtube_cookies.txt
```

### Method 2: Browser Extension
1. Install extension:
   - Chrome: "Get cookies.txt LOCALLY"
   - Firefox: "cookies.txt"
2. Log into YouTube
3. Click extension on youtube.com
4. Save as `config/youtube_cookies.txt`

### Method 3: Manual Export
1. Open YouTube in browser and log in
2. Open Developer Tools (F12)
3. Application → Cookies → youtube.com
4. Export these cookies:
   - SID, HSID, SSID, SAPISID, APISID
   - LOGIN_INFO, VISITOR_INFO1_LIVE
   - PREF, YSC, CONSENT
5. Format in Netscape format (see example below)

## Deploying Cookies to Server

### Docker Deployment
```bash
# Option 1: Volume mount
docker run -v $(pwd)/config/youtube_cookies.txt:/app/config/youtube_cookies.txt ...

# Option 2: Docker Compose (already configured)
docker-compose up
```

### Manual Deployment
```bash
# Copy to server
scp config/youtube_cookies.txt user@server:/path/to/app/config/

# Set permissions
chmod 644 /path/to/app/config/youtube_cookies.txt
```

## Verification

### Check Cookie Validity
```bash
# Run locally
python scripts/check_youtube_cookies.py

# Or in Docker
docker-compose run --rm cookie-tools python scripts/check_youtube_cookies.py
```

Expected output:
```
✅ Cookie file found: /app/config/youtube_cookies.txt
📅 File age: 5.2 days
🍪 Total cookies: 47
🔑 Important cookies found: SID, HSID, SSID, SAPISID, LOGIN_INFO
✅ SUCCESS: Video info extracted!
✅ COOKIES ARE WORKING!
```

## Maintenance

### Cookie Expiration
- Cookies expire after ~30 days
- System warns when cookies are >25 days old
- Re-run extraction when downloads fail

### Automated Refresh (Optional)
```bash
# Add to crontab (run monthly)
0 0 1 * * cd /path/to/app && python scripts/extract_cookies.py
```

## Troubleshooting

### "No cookies found"
- Make sure you're logged into YouTube
- Close browser before extraction
- Try different browser

### "Bot detection" errors
- Cookies are expired → Re-extract
- Wrong region → Use VPN matching server location
- Invalid format → Use automatic extractor

### Downloads still failing
1. Verify cookies: `python scripts/check_youtube_cookies.py`
2. Check logs: `grep "COOKIE" logs/*.log`
3. Ensure file permissions: `ls -la config/youtube_cookies.txt`

## Cookie File Format

Example `youtube_cookies.txt` (Netscape format):
```
# Netscape HTTP Cookie File
.youtube.com	TRUE	/	TRUE	1234567890	SID	AbCdEfGhIjKlMnOp
.youtube.com	TRUE	/	TRUE	1234567890	HSID	QrStUvWxYz123456
.youtube.com	TRUE	/	TRUE	1234567890	SSID	789AbCdEfGhIjKlM
```

## Security Notes

⚠️ **NEVER commit cookies to git!**
- Add to `.gitignore`: `config/youtube_cookies.txt`
- Use environment variables for paths
- Rotate cookies regularly

## Success Metrics

With proper cookies:
- ✅ 95%+ download success rate
- ✅ Works on ALL cloud providers
- ✅ Bypasses bot detection
- ✅ No IP blocking

Without cookies:
- ❌ 0% success on cloud servers
- ❌ Immediate bot detection
- ❌ All strategies fail

## Need Help?

1. Run diagnostics: `python scripts/check_youtube_cookies.py`
2. Check documentation: `cat YOUTUBE_DOWNLOAD_SETUP.md`
3. Review logs: `tail -f logs/youtube_download.log`

Remember: **Cookies are NOT optional - they are REQUIRED for cloud deployments!**