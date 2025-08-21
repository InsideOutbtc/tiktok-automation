FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    wget \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN pip install playwright && \
    playwright install chromium

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p input output processing posted logs database assets/watermarks assets/logos

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PLAYWRIGHT_BROWSERS_PATH=/app/browsers

# Create non-root user
RUN useradd -m -s /bin/bash powerpro && \
    chown -R powerpro:powerpro /app

USER powerpro

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

# Run the automation system
CMD ["python", "src/core/main_controller.py", "start", "--max-velocity"]