# COMPLETE DEPLOYMENT FIX PLAN

## CRITICAL FIXES (Must Do):

### 1. Fix Dockerfile CMD
```dockerfile
# Change from:
CMD ["python", "start_safe.py", "start", "--max-velocity"]

# To:
CMD ["python", "-m", "src.core.main_controller", "start"]
```

### 2. Fix requirements.txt
```diff
- TikTokApi==6.3.0  # Latest async version
- requests==2.31.0
+ requests==2.32.3  # Compatible with yt-dlp
```

### 3. Create start_safe.py (Alternative)
```python
#!/usr/bin/env python3
"""Safe startup wrapper"""
import sys
import os
sys.path.insert(0, '/app')

try:
    from src.core.main_controller import main
    import asyncio
    asyncio.run(main())
except Exception as e:
    print(f"Startup failed: {e}")
    # Run just the dashboard if main fails
    os.system("python src/api/simple_dashboard.py")
```

### 4. Fix cv2 Import in smart_clipper.py
```python
# Add at top of file:
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    print("Warning: cv2 not available, video analysis disabled")
    CV2_AVAILABLE = False
    cv2 = None
```

### 5. Fix Dashboard Port Conflict
```python
# In main_controller.py, change subprocess line to:
# Don't start dashboard here - let Docker handle it
```

## RECOMMENDED FIXES:

### 6. Simplify Dependencies
Remove from requirements.txt:
- playwright (not needed for MVP)
- scikit-learn (not used)
- pandas (not used)
- instaloader (not used)
- redis (not used)
- pytest packages (not needed in production)
- black, flake8, pre-commit (dev only)

### 7. Add Health Check Script
```python
# src/health_check.py
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

### 8. Update Dockerfile for Separate Services
```dockerfile
# Add at end:
EXPOSE 8000
# For web service mode
```

## DIGITALOCEAN APP SPEC FIX:

```yaml
services:
  - name: web
    dockerfile_path: Dockerfile
    source_dir: /
    github:
      branch: main
      deploy_on_push: true
      repo: InsideOutbtc/tiktok-automation
    http_port: 8000
    instance_count: 1
    instance_size_slug: basic-xxs
    routes:
      - path: /
    run_command: python src/api/simple_dashboard.py
    health_check:
      http_path: /health
      initial_delay_seconds: 10
      period_seconds: 10
      timeout_seconds: 5
      success_threshold: 1
      failure_threshold: 3
```

## EXECUTION STEPS:

1. Fix requirements.txt (remove TikTokApi, update requests)
2. Create start_safe.py
3. Fix cv2 imports
4. Remove dashboard subprocess from main_controller
5. Update Dockerfile CMD
6. Commit and push
7. Update DigitalOcean app spec
8. Deploy