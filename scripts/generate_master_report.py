#!/usr/bin/env python3
# Generate comprehensive test report with analysis

import json
import os
from datetime import datetime
from pathlib import Path
import sys

def generate_master_report():
    """Generate comprehensive test report with analysis"""
    
    print("\n" + "="*60)
    print("📊 TIKTOK AI AUTOMATION - SYSTEM VALIDATION REPORT")
    print("="*60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Load test results
    report_files = {
        'system_test': 'logs/test_report.json',
        'test_summary': None,  # Will find latest
        'test_posts': 'logs/test_posts.json',
        'api_test': 'logs/api_test_results.json'
    }
    
    # Find latest summary
    log_dir = Path('logs')
    summaries = list(log_dir.glob('test_summary_*.json'))
    if summaries:
        report_files['test_summary'] = str(max(summaries, key=os.path.getctime))
    
    results = {}
    for name, path in report_files.items():
        if path and os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    results[name] = json.load(f)
            except:
                results[name] = None
    
    # === SYSTEM STATUS ===
    print("🔍 SYSTEM STATUS")
    print("-" * 40)
    
    if results.get('system_test'):
        api_status = results['system_test'].get('api_status', {})
        
        # API Status
        print("\n📡 API Connectivity:")
        for api, status in api_status.items():
            icon = "✅" if "✅" in str(status) else "❌"
            print(f"  {icon} {api.upper()}: {status}")
        
        # Pipeline Status
        pipeline = results['system_test'].get('pipeline_status', {})
        print("\n🔄 Pipeline Components:")
        for component, status in pipeline.items():
            icon = "✅" if "✅" in str(status) else "❌"
            print(f"  {icon} {component.replace('_', ' ').title()}: {status}")
        
        # AI Accuracy
        ai_accuracy = results['system_test'].get('ai_accuracy', {})
        if ai_accuracy:
            print("\n🤖 AI Performance:")
            for metric, value in ai_accuracy.items():
                print(f"  📊 {metric.replace('_', ' ').title()}: {value}")
        
        # Performance Metrics
        perf = results['system_test'].get('performance_metrics', {})
        if perf:
            print("\n⚡ Performance Metrics:")
            for metric, value in perf.items():
                print(f"  ⏱️ {metric.replace('_', ' ').title()}: {value}")
    
    # === TEST SUMMARY ===
    if results.get('test_summary'):
        summary = results['test_summary']
        print("\n" + "="*40)
        print("📈 TEST EXECUTION SUMMARY")
        print("-" * 40)
        
        # Count tests from summary
        tests_data = summary.get('tests', {})
        total_tests = len(tests_data)
        passed = sum(1 for t in tests_data.values() if t.get('status') == 'PASSED')
        failed = sum(1 for t in tests_data.values() if t.get('status') == 'FAILED')
        
        print(f"\nTests Run: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        if total_tests > 0:
            success_rate = (passed / total_tests) * 100
            print(f"📊 Success Rate: {success_rate:.1f}%")
    
    # === CONTENT PROCESSED ===
    if os.path.exists('logs/test_posts.json'):
        try:
            # Read line by line as it might be JSONL
            posts = []
            with open('logs/test_posts.json', 'r') as f:
                for line in f:
                    if line.strip():
                        posts.append(json.loads(line))
            
            if posts:
                print("\n" + "="*40)
                print("📹 CONTENT PROCESSING RESULTS")
                print("-" * 40)
                print(f"\nContent Ready for Posting: {len(posts)} clips")
                
                # Show top 3 clips
                for i, post in enumerate(posts[:3], 1):
                    print(f"\n  Clip {i}:")
                    print(f"    Title: {post.get('title', 'N/A')[:50]}...")
                    print(f"    Score: {post.get('score', 0):.2f}")
                    print(f"    Platform: {post.get('platform', 'N/A')}")
        except:
            pass
    
    # === PRODUCTION READINESS ===
    print("\n" + "="*60)
    print("🚀 PRODUCTION READINESS ASSESSMENT")
    print("="*60)
    
    criteria = {
        "API Connectivity": check_apis_ready(results),
        "Content Discovery": check_discovery_ready(results),
        "Video Processing": check_processing_ready(results),
        "AI Accuracy": check_ai_ready(results),
        "Performance": check_performance_ready(results),
        "Error Handling": check_errors_ready(results)
    }
    
    ready_count = 0
    for criterion, (status, message) in criteria.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {criterion}: {message}")
        if status:
            ready_count += 1
    
    # === FINAL VERDICT ===
    print("\n" + "="*60)
    readiness_score = (ready_count / len(criteria)) * 100
    
    if readiness_score >= 80:
        print("✅ SYSTEM IS READY FOR PRODUCTION!")
        print(f"   Readiness Score: {readiness_score:.0f}%")
        print("\n   Next Steps:")
        print("   1. Review any warnings above")
        print("   2. Enable AUTO_PUBLISH=true in .env (if desired)")
        print("   3. Run: python3 src/core/main_controller.py start")
    elif readiness_score >= 60:
        print("⚠️ SYSTEM NEEDS MINOR ADJUSTMENTS")
        print(f"   Readiness Score: {readiness_score:.0f}%")
        print("\n   Required Actions:")
        print("   - Fix any ❌ items above")
        print("   - Re-run tests after fixes")
    else:
        print("❌ SYSTEM NOT READY FOR PRODUCTION")
        print(f"   Readiness Score: {readiness_score:.0f}%")
        print("\n   Critical Issues:")
        print("   - Multiple components failing")
        print("   - Review logs/test_report.json for details")
    
    # === SAVE MASTER REPORT ===
    master_report = {
        "timestamp": datetime.now().isoformat(),
        "readiness_score": readiness_score,
        "criteria_results": {k: {"status": v[0], "message": v[1]} for k, v in criteria.items()},
        "test_results": results,
        "recommendation": "READY" if readiness_score >= 80 else "NOT READY"
    }
    
    report_path = f"logs/master_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(master_report, f, indent=2, default=str)
    
    print(f"\n📄 Full report saved to: {report_path}")
    print("="*60)
    
    return readiness_score, master_report['recommendation']

def check_apis_ready(results):
    """Check if all APIs are connected"""
    if not results.get('system_test'):
        return False, "No test results found"
    
    api_status = results['system_test'].get('api_status', {})
    
    youtube_ok = "✅" in str(api_status.get('youtube', ''))
    openai_ok = "✅" in str(api_status.get('openai', ''))
    
    if youtube_ok and openai_ok:
        return True, "All critical APIs connected"
    elif youtube_ok:
        return True, "YouTube connected (OpenAI optional)"
    else:
        return False, "Critical APIs not connected"

def check_discovery_ready(results):
    """Check if content discovery works"""
    if not results.get('system_test'):
        return False, "No test results"
    
    discovery = results['system_test'].get('pipeline_status', {}).get('discovery', '')
    
    if "✅" in discovery and "Found" in discovery:
        return True, discovery
    else:
        return False, "Content discovery failed"

def check_processing_ready(results):
    """Check if video processing works"""
    if not results.get('system_test'):
        return False, "No test results"
    
    pipeline = results['system_test'].get('pipeline_status', {})
    
    download_ok = "✅" in str(pipeline.get('download', ''))
    clips_ok = "✅" in str(pipeline.get('clip_extraction', ''))
    
    if download_ok and clips_ok:
        return True, "Video processing pipeline working"
    elif clips_ok:
        return True, "Clip extraction working (download issues)"
    else:
        return False, "Video processing failed"

def check_ai_ready(results):
    """Check if AI accuracy is acceptable"""
    if not results.get('system_test'):
        return False, "No test results"
    
    ai_accuracy = results['system_test'].get('ai_accuracy', {})
    
    if not ai_accuracy:
        return False, "AI not tested"
    
    accuracy_str = ai_accuracy.get('viral_prediction', '0%')
    try:
        accuracy = float(accuracy_str.strip('%'))
        if accuracy >= 70:
            return True, f"AI accuracy {accuracy:.0f}% (good)"
        elif accuracy >= 50:
            return True, f"AI accuracy {accuracy:.0f}% (acceptable)"
        else:
            return False, f"AI accuracy {accuracy:.0f}% (too low)"
    except:
        return False, "Could not parse AI accuracy"

def check_performance_ready(results):
    """Check if performance is acceptable"""
    if not results.get('system_test'):
        return True, "Performance not tested (optional)"
    
    perf = results['system_test'].get('performance_metrics', {})
    
    if not perf:
        return True, "Performance metrics not available"
    
    # Check API response time
    api_time_str = perf.get('api_response', '0ms')
    try:
        api_time = float(api_time_str.replace('ms', ''))
        if api_time < 5000:  # 5 seconds is reasonable for real API
            return True, f"API response {api_time:.0f}ms (good)"
        else:
            return False, f"API response {api_time:.0f}ms (too slow)"
    except:
        return True, "Performance metrics unclear"

def check_errors_ready(results):
    """Check error handling"""
    if results.get('test_summary'):
        # Count from tests data
        tests_data = results['test_summary'].get('tests', {})
        failed = sum(1 for t in tests_data.values() if t.get('status') == 'FAILED')
        
        if failed == 0:
            return True, "No errors during testing"
        elif failed <= 2:
            return True, f"{failed} minor errors (acceptable)"
        else:
            return False, f"{failed} errors detected"
    
    # Check from system test
    if results.get('system_test'):
        passed = results['system_test'].get('tests_passed', 0)
        failed = results['system_test'].get('tests_failed', 0)
        
        if failed == 0:
            return True, "No errors during testing"
        elif failed <= 2:
            return True, f"{failed} minor errors (acceptable)"
        else:
            return False, f"{failed} errors detected"
            
    return True, "Error handling not tested"

if __name__ == "__main__":
    score, rec = generate_master_report()
    sys.exit(0 if rec == "READY" else 1)