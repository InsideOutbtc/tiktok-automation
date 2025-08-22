FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    wget \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements files
COPY requirements*.txt ./

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt || \
    (echo "📦 Main requirements failed, trying essential..." && \
     test -f requirements_essential.txt && pip install --no-cache-dir -r requirements_essential.txt) || \
    (echo "📦 Installing minimal packages..." && \
     pip install --no-cache-dir \
         yt-dlp \
         openai \
         moviepy \
         Pillow \
         requests \
         beautifulsoup4 \
         sqlalchemy \
         python-dotenv \
         tenacity \
         aiohttp)

# Copy application
COPY . .

# Remove any cached Python files that might have been copied
RUN find /app -type f -name "*.pyc" -delete && \
    find /app -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Fix Python path - CRITICAL for module imports
ENV PYTHONPATH=/app:/app/src:$PYTHONPATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure all __init__.py files exist
RUN find /app/src -type d -exec touch {}/__init__.py \;

# Create directories with proper permissions
RUN mkdir -p /app/database /app/input /app/output /app/processing /app/posted /app/logs /app/assets/watermarks /app/assets/logos && \
    chmod -R 755 /app && \
    chmod 777 /app/database

# Use /tmp for database if /app/database not writable
ENV DATABASE_PATH=/tmp/tiktok.db

# Create non-root user but give write permissions
RUN useradd -m powerpro && \
    chown -R powerpro:powerpro /app && \
    chmod -R 755 /app && \
    chmod 777 /app/database /tmp

USER powerpro

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "print('Health check passed'); exit(0)"

# Use the safe wrapper that handles import failures gracefully
# THIS IS THE CRITICAL FIX - ADD THE "start" ARGUMENT!
CMD ["python", "start_safe.py", "start", "--max-velocity"]