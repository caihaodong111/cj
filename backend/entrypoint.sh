#!/bin/bash
set -e

# Fix permissions for writable directories.
if [ -d /app/logs ]; then
    chmod 755 /app/logs
    if [ -f /app/logs/django.log ]; then
        chown appuser:appuser /app/logs/django.log 2>/dev/null || true
        chmod 644 /app/logs/django.log 2>/dev/null || true
    fi
fi

mkdir -p /app/data/qr_bridge
mkdir -p /app/crawler/browser_data /app/crawler/temp_image
chown -R appuser:appuser /app/logs /app/staticfiles /app/media /app/data /app/crawler/browser_data /app/crawler/temp_image 2>/dev/null || true

if [ "${RUN_DB_MIGRATIONS:-1}" = "1" ]; then
    gosu appuser:appuser python manage.py migrate --noinput
fi

if [ "${RUN_COLLECTSTATIC:-1}" = "1" ]; then
    gosu appuser:appuser python manage.py collectstatic --noinput
fi

exec gosu appuser:appuser "$@"
