# MediaCrawler Backend Dockerfile
# Multi-stage build with Chinese mirrors for faster package installation.

FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn \
    MEDIACRAWLER_QR_MODE=web \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN sed -i 's|deb.debian.org|mirrors.tuna.tsinghua.edu.cn|g; s|security.debian.org|mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        gcc \
        g++ \
        libffi-dev \
        libpq-dev \
        make && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Download Chromium into a fixed path so it can be copied into the runtime image.
# Do not use `playwright install-deps` here: on Debian trixie it falls back to
# an Ubuntu package list that includes unavailable font packages.
RUN playwright install chromium

FROM python:3.11-slim

LABEL maintainer="MediaCrawler" \
      description="MediaCrawler Backend Service"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=mediacrawler_config.settings \
    MEDIACRAWLER_QR_MODE=web \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN sed -i 's|deb.debian.org|mirrors.tuna.tsinghua.edu.cn|g; s|security.debian.org|mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        fonts-freefont-ttf \
        gosu \
        nodejs \
        fluxbox \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libatspi2.0-0 \
        libcairo2 \
        libcups2 \
        libdbus-1-3 \
        libdrm2 \
        libffi8 \
        libgbm1 \
        libnspr4 \
        libnss3 \
        libpango-1.0-0 \
        libpq5 \
        libu2f-udev \
        libvulkan1 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxext6 \
        libx11-6 \
        libx11-xcb1 \
        libxcb1 \
        libxcursor1 \
        libxi6 \
        libxkbcommon0 \
        libxrender1 \
        libxrandr2 \
        libxshmfence1 \
        novnc \
        websockify \
        x11vnc \
        xvfb && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /ms-playwright /ms-playwright

RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

COPY --chown=appuser:appuser . .

RUN mkdir -p /app/logs /app/staticfiles /app/media /app/data /app/data/qr_bridge \
    /app/crawler/browser_data /app/crawler/temp_image && \
    chown -R appuser:appuser /app/logs /app/staticfiles /app/media /app/data /app/crawler/browser_data /app/crawler/temp_image

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000 6080

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD curl -f http://localhost:8000/api/health || exit 1

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["gunicorn", "mediacrawler_config.wsgi:application", "--bind=0.0.0.0:8000", "--workers=3", "--threads=2", "--worker-class=sync", "--worker-tmp-dir=/dev/shm", "--timeout=120", "--keep-alive=30", "--max-requests=1000", "--max-requests-jitter=50", "--access-logfile=-", "--error-logfile=-", "--log-level=info"]
