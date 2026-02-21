#!/bin/bash
set -e

# Fix permissions for log directory
if [ -d /app/logs ]; then
    chmod 755 /app/logs
    # If log file exists but owned by root, fix it
    if [ -f /app/logs/django.log ]; then
        chown appuser:appuser /app/logs/django.log 2>/dev/null || true
        chmod 644 /app/logs/django.log 2>/dev/null || true
    fi
fi

# Ensure appuser owns the working directory
chown -R appuser:appuser /app/logs /app/staticfiles /app/media 2>/dev/null || true

# Execute the main container command as appuser
exec gosu appuser:appuser "$@"
