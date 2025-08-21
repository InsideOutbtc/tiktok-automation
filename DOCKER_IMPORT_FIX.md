# Docker Import Issue Analysis & Solution

## Problem Summary

The application runs successfully on macOS but fails in the Docker container (Ubuntu/Linux) with Python import errors, specifically:
- Database path `/app/database/tiktok.db` is created successfully
- Python imports fail immediately after, particularly `from src.database.queries import DatabaseQueries`

## Root Causes Identified

### 1. **Missing or Empty `__init__.py` Files**
- Docker's COPY command may not preserve empty `__init__.py` files
- Python requires these files to recognize directories as packages
- Linux is case-sensitive, unlike macOS

### 2. **Python Path Configuration**
- The PYTHONPATH needs both `/app` and `/app/src` for proper imports
- Docker container's working directory is `/app`, not the project root

### 3. **File Permissions**
- Files created on macOS may have different permissions in Linux
- The non-root user `powerpro` needs proper access

### 4. **Import Path Differences**
- macOS is case-insensitive, Linux is case-sensitive
- Relative vs absolute import paths behave differently

## Solutions Implemented

### 1. **Enhanced Dockerfile (`Dockerfile.fixed`)**
```dockerfile
# Ensures all __init__.py files exist
RUN touch /app/src/__init__.py && \
    touch /app/src/database/__init__.py && \
    # ... other __init__.py files

# Fixed Python path
ENV PYTHONPATH=/app:/app/src:$PYTHONPATH
```

### 2. **Import Fix Script (`fix_docker_imports.py`)**
- Automatically creates missing `__init__.py` files
- Fixes import statements in Python files
- Creates import helper for graceful fallbacks
- Verifies setup before deployment

### 3. **Enhanced Startup Script (`start_docker_safe.py`)**
- Diagnoses import environment before attempting imports
- Creates missing files on startup
- Provides detailed error messages
- Falls back to health check mode instead of crashing

### 4. **Debug Script (`docker_debug_imports.py`)**
- Tests imports step by step
- Shows Python path configuration
- Checks file permissions
- Identifies OS-specific issues

## Deployment Steps

1. **Run the fix script locally:**
   ```bash
   python3 fix_docker_imports.py
   ```

2. **Build the fixed Docker image:**
   ```bash
   docker build -f Dockerfile.fixed -t powerpro-fixed:latest .
   ```

3. **Test imports in container:**
   ```bash
   docker run --rm powerpro-fixed:latest python docker_debug_imports.py
   ```

4. **Run the container:**
   ```bash
   docker run -d \
     --name powerpro \
     -e YOUTUBE_API_KEY="your-key" \
     -e OPENAI_API_KEY="your-key" \
     -v $(pwd)/database:/app/database \
     powerpro-fixed:latest
   ```

5. **Deploy to DigitalOcean:**
   - Tag the image: `docker tag powerpro-fixed:latest registry.digitalocean.com/YOUR_REGISTRY/powerpro:latest`
   - Push: `docker push registry.digitalocean.com/YOUR_REGISTRY/powerpro:latest`
   - Update App Platform to use the new image

## Quick Deployment

Use the all-in-one deployment script:
```bash
./deploy_docker_fixed.sh
```

This script:
- Runs all fixes
- Builds the Docker image
- Tests imports
- Starts a test container
- Provides deployment instructions

## Verification

After deployment, verify the fix by checking logs:
```bash
docker logs -f powerpro
```

You should see:
- ✓ Database accessible
- ✓ DatabaseQueries imported successfully
- 🚀 Starting automation...

## Troubleshooting

If imports still fail:

1. **Check `__init__.py` files:**
   ```bash
   docker exec powerpro ls -la /app/src/__init__.py
   docker exec powerpro ls -la /app/src/database/__init__.py
   ```

2. **Verify Python path:**
   ```bash
   docker exec powerpro python -c "import sys; print(sys.path)"
   ```

3. **Test specific import:**
   ```bash
   docker exec powerpro python -c "from src.database.queries import DatabaseQueries; print('Success!')"
   ```

4. **Check file permissions:**
   ```bash
   docker exec powerpro ls -la /app/src/database/queries.py
   ```

## Prevention

To prevent future import issues:

1. Always ensure `__init__.py` files exist and are not empty
2. Use absolute imports: `from src.database.queries import ...`
3. Test in Docker locally before deploying
4. Include the diagnostic scripts in your CI/CD pipeline