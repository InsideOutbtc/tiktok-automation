#!/usr/bin/env python3
"""
Test the Daily Batch Processor with a smaller limit
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.daily_batch_processor import DailyBatchProcessor
import logging

def test_batch_processor():
    """Test with reduced limits"""
    processor = DailyBatchProcessor()
    
    # Override limits for testing
    processor.daily_limit = 3  # Only download 3 videos for testing
    processor.max_duration = 300  # Max 5 minutes
    
    logging.info("🧪 Testing Daily Batch Processor with 3 video limit")
    
    # Run the batch
    results = processor.run_daily_batch()
    
    print("\n✅ Test Complete!")
    print(f"Downloaded: {results['downloaded']} videos")
    print(f"Failed: {results['failed']} videos") 
    print(f"Clips created: {results['clips_created']}")
    print(f"Storage used: {results['storage_used_mb']:.1f} MB")
    
    return results

if __name__ == "__main__":
    test_batch_processor()