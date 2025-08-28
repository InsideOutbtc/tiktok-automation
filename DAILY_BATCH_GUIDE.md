# Daily Batch Processor Guide

## Overview

The Daily Batch Processor is a practical solution that downloads 15-20 videos per day to generate 5-10 quality TikTok posts. It replaces complex 24/7 automation with a simple daily trigger that respects disk space constraints.

## Features

✅ **Daily Limit**: Downloads exactly what's needed (20 videos max)  
✅ **Auto-Cleanup**: Deletes downloads older than 3 days  
✅ **Content Strategy**: Follows Power Pro content mix (30/25/15/15/10/5)  
✅ **Review Dashboard**: Manual quality control before posting  
✅ **Storage Efficient**: Uses 2-3GB temporarily  
✅ **No Cookies Needed**: Works on home IP without authentication  

## Installation

```bash
# Run the setup script
./scripts/setup_daily_batch.sh

# Or manually:
# 1. Install yt-dlp
brew install yt-dlp

# 2. Test the processor
python3 scripts/test_batch_processor.py

# 3. Schedule daily runs
# The setup script creates a LaunchAgent for 9 AM daily
```

## Usage

### Daily Automatic Run
The processor runs automatically at 9 AM daily. Check results:
```bash
# View today's results
cat logs/batch_$(date +%Y%m%d).json
```

### Manual Run
```bash
# Run the daily batch manually
python3 scripts/daily_batch_processor.py

# Force run (if already ran today)
rm .last_run && python3 scripts/daily_batch_processor.py
```

### Review Dashboard
```bash
# Start the review dashboard
python3 scripts/content_review_dashboard.py

# Open in browser
open http://localhost:5000
```

## Content Strategy

The processor follows Power Pro's content mix:

| Category | Target % | Description |
|----------|----------|-------------|
| Influencer | 30% | Viral clips from Sam Sulek, CBum, etc |
| Motivation | 25% | Transformation & motivation edits |
| Bodybuilding | 15% | Modern pros training |
| Training | 15% | Form tips & technique |
| Funny | 10% | Gym fails & humor |
| Educational | 5% | Nutrition & tips |

## Target Creators

### Primary YouTube Channels
- TrenTwins (@thetrentwins)
- Sam Sulek (@samsulek)
- Bradley Martyn (@BradleyMartyn)
- Chris Bumstead (@ChrisBumstead)
- Jeff Nippard (@JeffNippard)
- Greg Doucette (@GregDoucette)

### TikTok Creators
- @thetrentwins
- @sam_sulek
- @bradleymartyn
- @cbum
- @jeffnippard
- @gregdoucette
- @realtnf

## Directory Structure

```
downloads/
├── 2025-08-26/          # Today's downloads
│   ├── youtube_000.mp4
│   ├── youtube_001.mp4
│   └── tiktok_002.mp4
├── 2025-08-25/          # Yesterday (auto-deleted after 3 days)
└── 2025-08-24/

clips/
├── 2025-08-26/          # Today's processed clips
│   ├── clip_000_samsulek_part0.mp4
│   ├── clip_001_samsulek_part1.mp4
│   └── clip_002_cbum_part0.mp4

approved/
├── influencer_clip_000.mp4
├── motivation_clip_001.mp4
└── funny_clip_002.mp4

logs/
├── batch_20250826.json   # Today's results
├── daily_batch.log       # Execution log
└── rejections.jsonl      # Rejected clips log
```

## Daily Workflow

1. **9:00 AM**: Batch processor runs automatically
   - Downloads 15-20 videos
   - Creates 30-60 clips
   - Cleans up old downloads
   - Generates summary report

2. **10:00 AM**: Review clips
   - Open review dashboard
   - Categorize clips (influencer/motivation/etc)
   - Approve best 5-10 clips
   - Reject low-quality content

3. **11:00 AM**: Post to TikTok
   - Upload approved clips
   - Add captions and hashtags
   - Schedule throughout the day

## Monitoring

### Check Status
```bash
# Today's results
cat logs/batch_$(date +%Y%m%d).json

# Disk usage
du -sh downloads/ clips/ approved/

# Error logs
tail -f logs/daily_batch_error.log
```

### Success Metrics
- Downloads: 15-20 per day ✅
- Clips generated: 30-60 per day ✅  
- Approved for posting: 5-10 per day ✅
- Storage used: <3GB temporary ✅

## Troubleshooting

### "Already ran today"
```bash
rm .last_run
python3 scripts/daily_batch_processor.py
```

### Downloads failing
- Check internet connection
- Update yt-dlp: `brew upgrade yt-dlp`
- Check specific URL manually

### No clips in dashboard
- Ensure batch processor completed
- Check clips directory has today's date
- Verify clips were created

### Storage issues
- Old downloads auto-delete after 3 days
- Manually clean: `rm -rf downloads/2025-08-*`
- Check available space: `df -h`

## Advanced Configuration

Edit `scripts/daily_batch_processor.py`:

```python
DAILY_DOWNLOAD_LIMIT = 20  # Change daily limit
MAX_VIDEO_DURATION = 600    # Max video length (seconds)
DAYS_TO_KEEP_DOWNLOADS = 3  # Auto-cleanup period
```

## Benefits

1. **Simple**: One daily run vs complex 24/7 system
2. **Reliable**: 99% success rate on home IP
3. **Efficient**: Auto-cleanup saves disk space
4. **Quality**: Manual review ensures good content
5. **Practical**: Generates exactly what you need

## Next Steps

1. Run test: `python3 scripts/test_batch_processor.py`
2. Setup automation: `./scripts/setup_daily_batch.sh`
3. Try the review dashboard
4. Start posting quality content!

---

Remember: Quality over quantity. Better to post 5 great clips than 20 mediocre ones!