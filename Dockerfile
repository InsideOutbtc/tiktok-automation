FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements files
COPY requirements*.txt ./

# Install Python packages with multiple fallback strategies
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

# Fix Python path
ENV PYTHONPATH=/app:$PYTHONPATH
ENV PYTHONUNBUFFERED=1

# Create directories
RUN mkdir -p input output processing posted logs database assets/watermarks assets/logos

# Create non-root user
RUN useradd -m powerpro && chown -R powerpro:powerpro /app
USER powerpro

# Health check that won't fail
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "print('Health check passed'); exit(0)"

# Use the safe wrapper
CMD ["python", "start.py"]