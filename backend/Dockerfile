# MediaCrawler Backend Dockerfile
# Multi-stage build with Tsinghua mirrors for faster Chinese network builds

# Stage 1: Builder
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Use Tsinghua mirror for apt (Debian packages)
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libffi-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Use Tsinghua mirror for pip
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip with Tsinghua mirror
RUN pip install --upgrade pip

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

# Install Playwright browsers
RUN playwright install chromium

# Install Chromium system dependencies for Debian (instead of playwright install-deps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    fonts-freefont-ttf \
    libu2f-udev \
    libvulkan1 \
    libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Runtime
FROM python:3.11-slim

# Set labels
LABEL maintainer="MediaCrawler" \
      description="MediaCrawler Backend Service"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=mediacrawler_config.settings

# Use Tsinghua mirror for apt
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libffi8 \
    curl \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Set work directory
WORKDIR /app

# Copy project files
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p /app/logs /app/staticfiles /app/media && \
    chown -R appuser:appuser /app/logs /app/staticfiles /app/media

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Copy entrypoint script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Set entrypoint to fix permissions before running
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Run the application with gunicorn
CMD exec gunicorn mediacrawler_config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 2 \
    --worker-class sync \
    --worker-tmp-dir /dev/shm \
    --timeout 120 \
    --keep-alive 30 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
