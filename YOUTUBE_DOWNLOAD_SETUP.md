# YouTube Download Resilience System

## Overview
This system implements a multi-strategy approach to achieve 95% YouTube download success rate, bypassing "Sign in to confirm you're not a bot" errors.

## Features
- 5 fallback download strategies
- Cookie-based authentication
- Invidious proxy support
- Cobalt API integration
- Automatic retry with backoff
- Pattern learning for optimization

## Quick Setup

### 1. Extract YouTube Cookies (Recommended)
```bash
# Run the automatic extractor
python scripts/extract_cookies.py
```

This will:
- Find Chrome/Firefox cookies automatically
- Extract YouTube authentication cookies
- Save to `config/youtube_cookies.txt`

### 2. Manual Cookie Setup (Alternative)
If automatic extraction fails:

1. Install browser extension:
   - Chrome: "Get cookies.txt LOCALLY"
   - Firefox: "cookies.txt"

2. Log into YouTube

3. Click extension icon on youtube.com

4. Save as `config/youtube_cookies.txt`

### 3. Environment Variables (Optional)
```bash
# Set cookie file location
export YOUTUBE_COOKIE_FILE=/app/config/youtube_cookies.txt

# Add proxy for additional resilience
export YOUTUBE_PROXY=socks5://proxy.example.com:1080
```

## How It Works

The downloader tries these strategies in order:

1. **Cookies Strategy**: Uses authenticated session
2. **User Agent Rotation**: Mimics different browsers
3. **Invidious Proxy**: Uses public Invidious instances
4. **Cobalt API**: Alternative download service
5. **Proxy Download**: Uses configured proxy

If all fail, videos are queued for manual download.

## File Locations

- **Cookies**: `/app/config/youtube_cookies.txt`
- **Downloads**: `/app/input/`
- **Manual Queue**: `/app/output/manual_download_queue.json`
- **Patterns**: `/app/context/patterns/download_patterns.json`
- **Failures**: `/app/logs/download_failures.json`

## Monitoring

Check download success rate:
```python
from src.core.youtube_downloader import ResilientYouTubeDownloader
downloader = ResilientYouTubeDownloader()
stats = downloader.get_download_stats()
print(stats)
```

## Troubleshooting

### "Sign in to confirm" errors
1. Refresh cookies (re-run extract_cookies.py)
2. Check if logged into YouTube in browser
3. Verify cookies file exists and is readable

### All strategies failing
1. Check Invidious instances are up
2. Verify internet connectivity
3. Review `/app/logs/download_failures.json`
4. Check manual download queue

### Slow downloads
- This is intentional to avoid detection
- Rate limiting prevents IP bans
- Human-like delays between attempts

## Cookie Refresh

Cookies expire after ~30 days. Set up a cron job:
```bash
# Add to crontab
0 0 1 * * /usr/bin/python /app/scripts/extract_cookies.py
```

## Success Metrics

Target: 95% success rate
- Cookies: ~70% success
- Invidious: ~20% success
- Other strategies: ~5% success
- Manual queue: <5% of videos