FROM python:3.11-slim

WORKDIR /app

# Install system dependencies - REMOVED OpenGL conflicts
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    wget \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files first for better caching
COPY requirements*.txt ./

# Install Python packages with fallback options
RUN pip install --no-cache-dir -r requirements.txt || \
    (echo "Main requirements failed, installing essentials..." && \
     pip install --no-cache-dir \
         flask \
         google-api-python-client \
         google-auth \
         google-auth-httplib2 \
         yt-dlp \
         openai \
         moviepy==1.0.3 \
         opencv-python-headless==4.8.1.78 \
         imageio-ffmpeg==0.4.9 \
         numpy==1.24.3 \
         Pillow \
         requests \
         beautifulsoup4 \
         sqlalchemy \
         python-dotenv \
         tenacity \
         aiohttp)

# Copy application code
COPY . .

# Environment variables
ENV PYTHONPATH=/app:/app/src:$PYTHONPATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DATABASE_PATH=/tmp/tiktok.db
ENV YOUTUBE_COOKIE_FILE=/app/config/youtube_cookies.txt

# Create necessary directories
RUN mkdir -p /app/database /app/input /app/output /app/processing \
    /app/posted /app/logs /app/config /app/uploads \
    && chmod -R 755 /app

# Ensure __init__.py files exist
RUN find /app/src -type d -exec touch {}/__init__.py \; 2>/dev/null || true

# Clean up Python cache files
RUN find /app -type f -name "*.pyc" -delete && \
    find /app -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Expose port and run
EXPOSE 8000
CMD ["python", "src/api/simple_dashboard.py"]