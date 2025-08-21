# PowerPro TikTok Automation - Deployment Guide

## 🚀 Quick Start

### Prerequisites
- GitHub account
- DigitalOcean account
- API keys ready (YouTube, OpenAI)

### Step 1: Prepare Environment
```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Step 2: Test Locally
```bash
# Build and test with Docker
docker build -t powerpro-test .
docker run --env-file .env powerpro-test
```

### Step 3: Push to GitHub
```bash
git add .
git commit -m "PowerPro deployment ready"
git push origin main
```

### Step 4: Deploy to DigitalOcean
1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click "Create App"
3. Connect your GitHub repo
4. DigitalOcean will detect the `app.yaml`
5. Add environment variables:
   - YOUTUBE_API_KEY
   - OPENAI_API_KEY
6. Deploy!

## 📁 Project Structure
```
├── input/          # Source videos (auto-populated)
├── output/         # Generated clips
├── processing/     # Temporary files
├── posted/         # Archive of posted content
├── logs/           # Application logs
├── database/       # SQLite database
├── assets/
│   ├── logos/      # PowerPro logos
│   └── watermarks/ # Video watermarks
└── config/
    └── config.yaml # PowerPro configuration
```

## 🎯 Configuration
The system is pre-configured for PowerPro with:
- Brand colors: Orange (#FF6B35) & Blue (#004E89)
- Content mix: 30% viral clips, 25% motivation, etc.
- Posting schedule: 9AM, 12PM, 6PM, 9PM EST
- Watermark: Bottom-right corner

## 🔧 Customization
Edit `config/config.yaml` to adjust:
- Content strategy percentages
- Influencers to monitor
- Posting schedule
- Video settings

## 📊 Monitoring
- Health check: `/health`
- Logs: Check `logs/` directory
- Database: SQLite in `database/`

## 🚨 Troubleshooting
1. **Logo issues**: Re-run `python3 scripts/process_logos.py`
2. **Database errors**: Check permissions on `database/` directory
3. **API errors**: Verify your API keys in `.env`

## 💰 Costs
- DigitalOcean Basic: $12/month
- Storage: ~$5/month
- Total: ~$17/month

## 🎉 Success!
Once deployed, the system will:
1. Find trending fitness content
2. Extract best clips
3. Add PowerPro watermark
4. Post automatically 4x daily
5. Run 24/7 without intervention

Monitor your growth at: https://www.tiktok.com/@powerpro.social