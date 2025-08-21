#!/usr/bin/env python3
# Test Script for Real API Connections
# Tests YouTube, TikTok, OpenAI, and video downloading

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.content_sourcer import ContentSourcer
from src.agents.content_agents.viral_scout import ViralScoutAgent
from src.agents.content_agents.hook_writer import HookWriterAgent
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_youtube_api(sourcer: ContentSourcer):
    """Test YouTube API connection"""
    print("\n📺 Testing YouTube API...")
    
    if not sourcer.youtube:
        print("❌ YouTube API not configured (missing YOUTUBE_API_KEY)")
        return False
        
    try:
        videos = await sourcer._discover_youtube_real(["fitness"])
        if videos:
            print(f"✅ YouTube API working! Found {len(videos)} videos")
            print(f"   Example: {videos[0]['title'][:60]}...")
            print(f"   Views: {videos[0]['views']:,}")
            print(f"   Engagement: {videos[0]['engagement_score']:.2%}")
            return True
        else:
            print("⚠️ YouTube API connected but no videos found")
            return False
    except Exception as e:
        print(f"❌ YouTube API error: {e}")
        return False


async def test_tiktok_api(sourcer: ContentSourcer):
    """Test TikTok free API"""
    print("\n🎵 Testing TikTok (free API)...")
    
    try:
        videos = await sourcer._discover_tiktok_free(["fitness"])
        if videos:
            print(f"✅ TikTok API working! Found {len(videos)} videos")
            if videos:
                print(f"   Example: {videos[0]['title'][:60]}...")
                print(f"   Views: {videos[0]['views']:,}")
            return True
        else:
            print("⚠️ TikTok API connected but no videos found")
            return False
    except Exception as e:
        print(f"❌ TikTok API error: {e}")
        print("   Note: TikTok API may require additional setup")
        return False


async def test_video_download(sourcer: ContentSourcer):
    """Test video downloading"""
    print("\n📥 Testing video download...")
    
    # Create a test video object
    test_video = {
        "platform": "youtube",
        "id": "dQw4w9WgXcQ",  # Rick Roll for testing
        "title": "Test Video Download",
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    }
    
    try:
        path = await sourcer.download_video(test_video)
        if path and os.path.exists(path):
            size = os.path.getsize(path) / (1024 * 1024)  # MB
            print(f"✅ Download working! Video saved to: {path}")
            print(f"   File size: {size:.2f} MB")
            
            # Clean up test file
            try:
                os.remove(path)
                print("   Test file cleaned up")
            except:
                pass
                
            return True
        else:
            print("❌ Download failed - no file created")
            return False
    except Exception as e:
        print(f"❌ Download error: {e}")
        return False


async def test_openai_integration():
    """Test OpenAI API integration"""
    print("\n🤖 Testing OpenAI API...")
    
    try:
        import openai
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            print("❌ OpenAI API key not found (OPENAI_API_KEY)")
            return False
            
        openai.api_key = api_key
        
        # Simple test
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'API working' in 3 words"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ OpenAI API working! Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return False


async def test_ai_agents():
    """Test AI agent integration"""
    print("\n🧠 Testing AI Agents...")
    
    # Test Viral Scout
    scout = ViralScoutAgent()
    await scout.initialize()
    
    test_content = {
        "platform": "tiktok",
        "title": "Amazing 30-day transformation",
        "views": 1500000,
        "likes": 250000,
        "comments": 15000,
        "duration": 28,
        "engagement_score": 0.18
    }
    
    result = await scout.analyze(test_content)
    print(f"✅ Viral Scout working!")
    print(f"   Analysis method: {result.get('method', 'unknown')}")
    print(f"   Viral score: {result.get('score', 0):.2f}")
    print(f"   Top factor: {result.get('top_factor', 'unknown')}")
    
    # Test Hook Writer
    hook_writer = HookWriterAgent()
    await hook_writer.initialize()
    
    test_clip = {
        "platform": "tiktok",
        "type": "transformation",
        "duration": 30,
        "viral_score": 0.85
    }
    
    metadata = await hook_writer.generate_metadata(test_clip)
    print(f"\n✅ Hook Writer working!")
    print(f"   Title: {metadata['title']}")
    print(f"   Hook: {metadata['hook_text']}")
    print(f"   Generated by: {metadata.get('generated_by', 'unknown')}")
    
    return True


async def test_full_pipeline():
    """Test complete discovery pipeline"""
    print("\n🔄 Testing Full Discovery Pipeline...")
    
    sourcer = ContentSourcer()
    
    try:
        # Discover content
        content = await sourcer.discover_viral_content(
            platforms=["youtube"],
            keywords=["fitness", "workout"],
            limit=5
        )
        
        if content:
            print(f"✅ Full pipeline working! Found {len(content)} videos")
            
            # Show top video
            top = content[0]
            print(f"\n📊 Top Video:")
            print(f"   Title: {top.get('title', 'Unknown')[:60]}...")
            print(f"   Platform: {top['platform']}")
            print(f"   Views: {top.get('views', 0):,}")
            print(f"   Engagement: {top.get('engagement_score', 0):.2%}")
            if 'ai_score' in top:
                print(f"   AI Score: {top['ai_score']:.2f}")
                print(f"   AI Analysis: {top.get('ai_analysis', 'N/A')[:100]}...")
                
            return True
        else:
            print("❌ Pipeline failed - no content discovered")
            return False
            
    except Exception as e:
        print(f"❌ Pipeline error: {e}")
        return False


async def main():
    """Run all API tests"""
    print("🧪 TikTok AI Automation - API Connection Test")
    print("=" * 50)
    
    # Check environment
    print("\n🔐 Environment Check:")
    env_vars = {
        "YOUTUBE_API_KEY": "YouTube Discovery",
        "OPENAI_API_KEY": "AI Analysis",
        "TIKTOK_COOKIES_FILE": "TikTok Downloads (optional)"
    }
    
    for var, purpose in env_vars.items():
        if os.getenv(var):
            print(f"✅ {var} is set ({purpose})")
        else:
            print(f"❌ {var} not found ({purpose})")
    
    # Initialize content sourcer
    sourcer = ContentSourcer()
    
    # Run tests
    results = {
        "YouTube API": await test_youtube_api(sourcer),
        "TikTok API": await test_tiktok_api(sourcer),
        "Video Download": await test_video_download(sourcer),
        "OpenAI API": await test_openai_integration(),
        "AI Agents": await test_ai_agents(),
        "Full Pipeline": await test_full_pipeline()
    }
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System ready for real content.")
    elif passed > 0:
        print("\n⚠️ Some tests failed. Check your API keys and configuration.")
    else:
        print("\n❌ All tests failed. Please check your setup.")
    
    # Next steps
    print("\n📋 Next Steps:")
    if results["YouTube API"] or results["TikTok API"]:
        print("1. Run discovery: python src/core/main_controller.py discover")
    if results["Full Pipeline"]:
        print("2. Start full system: python src/core/main_controller.py start")
    print("3. Monitor logs in: logs/")


if __name__ == "__main__":
    asyncio.run(main())