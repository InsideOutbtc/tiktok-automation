#!/bin/bash
# Force a clean build on DigitalOcean by making a small change

echo "Forcing clean build on DigitalOcean..."

# Clean local Python cache files first
echo "Cleaning local Python cache..."
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Add a build timestamp to force cache invalidation
echo "# Build timestamp: $(date +%s)" >> Dockerfile
git add Dockerfile .dockerignore

# Commit with timestamp to force rebuild
git commit -m "Force clean rebuild - $(date +%Y%m%d-%H%M%S)"

echo "Changes committed. Push to trigger rebuild:"
echo "git push origin main"
echo ""
echo "After pushing, monitor the build logs in DigitalOcean dashboard to ensure:"
echo "1. The .dockerignore is being used (no .pyc files copied)"
echo "2. The cache cleaning step runs successfully"
echo "3. The new error_handler.py is being used"