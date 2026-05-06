#!/bin/bash
set -e

start_remote_desktop() {
    export DISPLAY="${XVFB_DISPLAY:-:99}"
    export VNC_PORT="${VNC_PORT:-5900}"
    export NOVNC_PORT="${NOVNC_PORT:-6080}"
    export XVFB_SCREEN="${XVFB_SCREEN:-1600x900x24}"

    mkdir -p /app/logs /tmp/.X11-unix
    rm -f "/tmp/.X${DISPLAY#:}-lock"

    Xvfb "${DISPLAY}" -screen 0 "${XVFB_SCREEN}" -ac +extension RANDR >/app/logs/xvfb.log 2>&1 &
    sleep 1

    fluxbox >/app/logs/fluxbox.log 2>&1 &

    if [ -n "${VNC_PASSWORD:-}" ]; then
        mkdir -p /app/.vnc
        x11vnc -storepasswd "${VNC_PASSWORD}" /app/.vnc/passwd >/dev/null 2>&1
        x11vnc \
            -display "${DISPLAY}" \
            -forever \
            -shared \
            -rfbport "${VNC_PORT}" \
            -rfbauth /app/.vnc/passwd \
            >/app/logs/x11vnc.log 2>&1 &
    else
        x11vnc \
            -display "${DISPLAY}" \
            -forever \
            -shared \
            -rfbport "${VNC_PORT}" \
            -nopw \
            >/app/logs/x11vnc.log 2>&1 &
    fi

    /usr/share/novnc/utils/novnc_proxy \
        --listen "${NOVNC_PORT}" \
        --vnc "127.0.0.1:${VNC_PORT}" \
        >/app/logs/novnc.log 2>&1 &
}

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

if [ "${ENABLE_REMOTE_DESKTOP:-1}" = "1" ]; then
    start_remote_desktop
fi

if [ "${RUN_DB_MIGRATIONS:-1}" = "1" ]; then
    gosu appuser:appuser python manage.py migrate --noinput
fi

if [ "${RUN_COLLECTSTATIC:-1}" = "1" ]; then
    gosu appuser:appuser python manage.py collectstatic --noinput
fi

exec gosu appuser:appuser "$@"
