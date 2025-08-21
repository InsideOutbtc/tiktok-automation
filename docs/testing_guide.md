# System Testing & Validation Guide

This guide covers how to test the TikTok AI Automation System before production use.

## 🚀 Quick Test

Run all tests automatically:
```bash
python scripts/run_all_tests.py
```

This will execute all tests in sequence and generate a comprehensive report.

## 📋 Manual Testing Steps

### 1. Pre-Test Setup
```bash
python scripts/pre_test_setup.py
```
- Checks environment configuration
- Validates API keys in .env
- Creates necessary directories
- Cleans old test data

### 2. API Connectivity Test
```bash
python scripts/test_apis.py
```
- Tests YouTube API connection
- Tests OpenAI API connection
- Tests TikTok discovery
- Downloads a test video
- Generates sample AI analysis

### 3. System Validation
```bash
python scripts/system_test.py
```
- Tests complete pipeline
- Discovers real content
- Downloads videos
- Extracts clips
- Tests AI predictions
- Validates scheduling
- Measures performance

### 4. Test Mode Run
```bash
python scripts/test_mode.py
```
- Runs system for 5 minutes
- Processes real videos
- NO actual posting
- Generates activity report

## ✅ Test Checklist

### Environment Setup
- [ ] Python 3.9+ installed
- [ ] FFmpeg installed
- [ ] All packages from requirements.txt installed
- [ ] .env file created with API keys
- [ ] YouTube API key added
- [ ] OpenAI API key added (optional but recommended)

### API Tests
- [ ] YouTube returns real videos
- [ ] Videos download successfully
- [ ] OpenAI generates analyses (if key provided)
- [ ] TikTok discovery works (may be limited)

### Processing Tests
- [ ] Videos download to input/downloads/
- [ ] Clips extract to processing/clips/
- [ ] AI agents make decisions
- [ ] Metadata generates correctly

### Performance Tests
- [ ] API responses reasonable
- [ ] Video processing under 1 minute
- [ ] No memory leaks
- [ ] No crashes during 5-minute test

## 📊 Expected Results

### Successful Test Output
```
✅ Tests Passed: 8/8
✅ SYSTEM READY FOR PRODUCTION

Downloaded Files: 2-3 videos
Generated Clips: 3-9 clips
Would Have Posted: 1-3 clips
```

### Test Reports Location
- `logs/test_report.json` - Detailed test results
- `logs/test_summary_*.json` - Overall summary
- `logs/test_posts.json` - What would have been posted
- `logs/test_mode.log` - Test mode activity

## 🚨 Common Issues

### Issue: No videos discovered
**Solution**: Check YouTube API key is valid and has quota

### Issue: Download fails
**Solution**: 
- Check internet connection
- Try with shorter videos
- Check yt-dlp is updated: `pip install --upgrade yt-dlp`

### Issue: No clips extracted
**Solution**:
- Check FFmpeg is installed: `ffmpeg -version`
- Check video downloaded correctly
- Review logs for errors

### Issue: AI analysis fails
**Solution**: Check OpenAI API key and credits

## 🎯 Test Success Criteria

The system is ready for production when:

1. **All APIs connect** successfully
2. **Videos download** without errors
3. **Clips extract** from videos
4. **AI makes decisions** about content
5. **No posts made** during testing (safety check)
6. **Performance acceptable** (<1 min per video)
7. **No critical errors** in logs

## 📈 Performance Benchmarks

### Good Performance
- API Discovery: <3 seconds
- Video Download: <30 seconds per video
- Clip Extraction: <30 seconds per video
- AI Analysis: <2 seconds per video
- Total Pipeline: <2 minutes per video

### Acceptable Performance
- API Discovery: <10 seconds
- Video Download: <60 seconds per video
- Clip Extraction: <60 seconds per video
- AI Analysis: <5 seconds per video
- Total Pipeline: <5 minutes per video

## 🔄 After Testing

### If All Tests Pass
1. Review generated clips in `processing/clips/`
2. Check `logs/test_posts.json` for what would be posted
3. Adjust viral thresholds if needed in config
4. Enable AUTO_PUBLISH=true when ready

### If Tests Fail
1. Check specific error messages
2. Review logs in `logs/` directory
3. Fix issues (usually API keys or dependencies)
4. Re-run failed tests only

## 🛡️ Safety Features

During testing:
- **No actual posts** to TikTok
- **Limited downloads** (max 3 videos)
- **Time limited** (5 minute test runs)
- **Safe mode** enabled
- **Mock posting** only

## 📞 Troubleshooting

### Enable Debug Logging
Add to .env:
```
DEBUG=true
LOG_LEVEL=DEBUG
```

### Check Specific Component
```bash
# Test only discovery
python -c "from src.core.content_sourcer import ContentSourcer; import asyncio; asyncio.run(ContentSourcer().discover_viral_content(['youtube'], ['fitness']))"
```

### View Recent Logs
```bash
tail -n 100 logs/test_mode.log
```

## ✨ Next Steps

After successful testing:

1. **Fine-tune Settings**
   - Adjust engagement thresholds
   - Set posting schedule
   - Configure platforms

2. **Monitor Initial Runs**
   - Start with AUTO_PUBLISH=false
   - Review what would be posted
   - Enable posting when confident

3. **Scale Gradually**
   - Start with 1-2 posts per day
   - Monitor performance
   - Increase as needed

Remember: The system uses Constitutional AI principles - it will run autonomously with Maximum Velocity Mode once enabled!