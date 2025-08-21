# Real API Integration Guide

This guide explains how to set up and use real APIs with the TikTok AI Automation System.

## 🚀 Quick Start

1. **Install Dependencies**
```bash
pip install -r requirements.txt
python -m playwright install  # Required for TikTok
```

2. **Set Up Environment Variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Test APIs**
```bash
python scripts/test_apis.py
```

4. **Start System**
```bash
# Full system
python src/core/main_controller.py start

# Discovery only
python src/core/main_controller.py discover

# Processing only
python src/core/main_controller.py process
```

## 🔑 API Setup

### YouTube API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Add to `.env`: `YOUTUBE_API_KEY=your_key_here`

**Free Quota**: 10,000 units/day (approx 100-200 searches)

### OpenAI API
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create account and add payment method
3. Generate API key
4. Add to `.env`: `OPENAI_API_KEY=your_key_here`

**Cost**: ~$0.002 per video analysis

### TikTok (Free Method)
The system uses TikTokApi which doesn't require official API access.

**Note**: May require cookies for better access:
1. Export cookies from browser
2. Save to file
3. Add to `.env`: `TIKTOK_COOKIES_FILE=/path/to/cookies.txt`

## 📊 API Features

### Content Discovery
- **YouTube**: Search by keywords, get video stats, filter by duration
- **TikTok**: Browse by hashtag, get trending videos
- **Filtering**: Automatic viral potential scoring

### AI Analysis
- **Viral Scoring**: GPT analyzes each video's potential
- **Hook Generation**: AI creates viral titles and descriptions
- **Performance Prediction**: ML-based view predictions

### Video Downloading
- **yt-dlp**: Downloads from YouTube, TikTok, and more
- **Quality Control**: Max 1080p to save bandwidth
- **Concurrent Downloads**: Up to 3 at once

## 🎯 Usage Examples

### Discover Viral Content
```python
from src.core.content_sourcer import ContentSourcer

sourcer = ContentSourcer()
videos = await sourcer.discover_viral_content(
    platforms=["youtube", "tiktok"],
    keywords=["fitness", "workout"],
    limit=20
)
```

### Download Videos
```python
for video in videos:
    if video['engagement_score'] > 0.7:
        path = await sourcer.download_video(video)
        print(f"Downloaded: {path}")
```

### AI Analysis
```python
from src.agents.content_agents.viral_scout import ViralScoutAgent

scout = ViralScoutAgent()
result = await scout.analyze(video)
print(f"Viral potential: {result['score']}")
```

## 🚨 Rate Limits & Best Practices

### YouTube
- **Quota**: 10,000 units/day
- **Search cost**: 100 units
- **Video details**: 3 units
- **Best practice**: Cache results, batch requests

### OpenAI
- **Rate limit**: 60 requests/minute (GPT-3.5)
- **Token limit**: 90,000 tokens/minute
- **Best practice**: Batch analyze videos, use concise prompts

### TikTok
- **No official limits** (using free API)
- **Best practice**: Add delays between requests, use cookies

## 🛠️ Troubleshooting

### YouTube API Issues
```bash
# Check quota
curl "https://www.googleapis.com/youtube/v3/search?part=snippet&q=test&key=YOUR_KEY"

# Common errors:
# 403: Quota exceeded or API not enabled
# 401: Invalid API key
```

### TikTok Issues
```bash
# If TikTok fails, try:
1. Update TikTokApi: pip install --upgrade TikTokApi
2. Use cookies from browser
3. Use VPN if blocked in your region
```

### OpenAI Issues
```bash
# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY"
```

## 📈 Performance Tips

1. **Caching**: Results are cached for 15 minutes
2. **Batch Processing**: Process multiple videos together
3. **Concurrent Downloads**: Adjust `max_concurrent` in config
4. **Token Optimization**: AI prompts are optimized for cost

## 🔒 Security Notes

- **Never commit .env file** (it's in .gitignore)
- **API keys are loaded from environment** only
- **No keys are logged or stored** in database
- **Use read-only API keys** when possible

## 📋 Next Steps

1. Monitor API usage in logs
2. Set up rate limit alerts
3. Implement quota management
4. Add more platforms (Instagram, etc.)

For more details, see the main [README.md](../README.md)