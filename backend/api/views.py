# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

"""
Django API views for MediaCrawler Backend
"""

import os
import json
import subprocess
import sys
import time
import threading
from collections import deque
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# Data directory
DATA_DIR = Path(__file__).parent.parent.parent / "data"
PROJECT_ROOT = settings.BASE_DIR.parent
CRAWLER_ROOT = settings.BASE_DIR / "crawler"

CRAWLER_LOCK = threading.Lock()
CRAWLER_PROCESS = None
CRAWLER_LOGS = deque(maxlen=2000)
CRAWLER_STATE = {
    "platform": "xhs",
    "login_type": "qrcode",
    "crawler_type": "search",
}


def _build_run_cmd(args):
    """Build command to run main.py via the current Python executable."""
    return [sys.executable, str(CRAWLER_ROOT / "main.py"), *args]


def _append_log(level: str, message: str):
    with CRAWLER_LOCK:
        CRAWLER_LOGS.append({
            "level": level,
            "message": message,
            "timestamp": time.time(),
        })


def _get_process():
    with CRAWLER_LOCK:
        return CRAWLER_PROCESS


def _set_process(process):
    with CRAWLER_LOCK:
        global CRAWLER_PROCESS
        CRAWLER_PROCESS = process


def _get_logs():
    with CRAWLER_LOCK:
        return list(CRAWLER_LOGS)


def _update_state(platform: str, login_type: str, crawler_type: str):
    with CRAWLER_LOCK:
        CRAWLER_STATE["platform"] = platform
        CRAWLER_STATE["login_type"] = login_type
        CRAWLER_STATE["crawler_type"] = crawler_type


def _get_state():
    with CRAWLER_LOCK:
        return dict(CRAWLER_STATE)


def _stream_pipe(pipe, level: str):
    try:
        for line in iter(pipe.readline, ""):
            if not line:
                break
            _append_log(level, line.rstrip())
    finally:
        try:
            pipe.close()
        except Exception:
            pass


# ============== Health Check ==============

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    return Response({"status": "ok"})


@api_view(['GET'])
@permission_classes([AllowAny])
def check_environment(request):
    """Check if MediaCrawler environment is configured correctly"""
    try:
        # Run main.py --help to check environment
        process = subprocess.run(
            _build_run_cmd(["--help"]),
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=30
        )

        if process.returncode == 0:
            return Response({
                "success": True,
                "message": "MediaCrawler environment configured correctly",
                "output": process.stdout[:500]  # Truncate to first 500 characters
            })
        else:
            error_msg = process.stderr or process.stdout
            return Response({
                "success": False,
                "message": "Environment check failed",
                "error": error_msg[:500]
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except subprocess.TimeoutExpired:
        return Response({
            "success": False,
            "message": "Environment check timeout",
            "error": "Command execution exceeded 30 seconds"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({
            "success": False,
            "message": "Environment check error",
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_platforms(request):
    """Get list of supported platforms"""
    return Response({
        "platforms": [
            {"value": "xhs", "label": "Xiaohongshu", "icon": "book-open"},
            {"value": "dy", "label": "Douyin", "icon": "music"},
            {"value": "ks", "label": "Kuaishou", "icon": "video"},
            {"value": "bili", "label": "Bilibili", "icon": "tv"},
            {"value": "wb", "label": "Weibo", "icon": "message-circle"},
            {"value": "tieba", "label": "Baidu Tieba", "icon": "messages-square"},
            {"value": "zhihu", "label": "Zhihu", "icon": "help-circle"},
        ]
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_config_options(request):
    """Get all configuration options"""
    return Response({
        "login_types": [
            {"value": "qrcode", "label": "QR Code Login"},
            {"value": "cookie", "label": "Cookie Login"},
        ],
        "crawler_types": [
            {"value": "search", "label": "Search Mode"},
            {"value": "detail", "label": "Detail Mode"},
            {"value": "creator", "label": "Creator Mode"},
        ],
        "save_options": [
            {"value": "json", "label": "JSON File"},
            {"value": "csv", "label": "CSV File"},
            {"value": "excel", "label": "Excel File"},
            {"value": "sqlite", "label": "SQLite Database"},
            {"value": "db", "label": "MySQL Database"},
            {"value": "mongodb", "label": "MongoDB Database"},
        ],
    })


# ============== Crawler Control ==============

class CrawlerView(APIView):
    """Crawler control views"""

    permission_classes = [AllowAny]

    def post(self, request, action=None):
        """Handle crawler actions: start, stop"""
        if action == "start":
            return self._start_crawler(request)
        elif action == "stop":
            return self._stop_crawler()
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, action=None):
        """Get crawler status or logs"""
        if action == "status":
            return self._get_status()
        elif action == "logs":
            limit = int(request.GET.get("limit", 100))
            return self._get_logs(limit)
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

    def _start_crawler(self, request):
        """Start crawler task"""
        current_process = _get_process()
        if current_process and current_process.poll() is None:
            return Response(
                {"error": "Crawler is already running"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = request.data
            platform = data.get("platform", "xhs")
            login_type = data.get("login_type", "qrcode")
            crawler_type = data.get("crawler_type", "search")
            _update_state(platform, login_type, crawler_type)

            # Build command
            cmd_args = [
                "--platform", platform,
                "--lt", login_type,
                "--type", crawler_type,
                "--save_data_path", str(DATA_DIR),
            ]

            # Add optional parameters
            if keywords := data.get("keywords"):
                cmd_args.extend(["--keywords", keywords])
            if save_option := data.get("save_option"):
                cmd_args.extend(["--save_data_option", save_option])
            if start_page := data.get("start_page"):
                cmd_args.extend(["--start", str(start_page)])
            if cookies := data.get("cookies"):
                cmd_args.extend(["--cookies", cookies])
            if specified_ids := data.get("specified_ids"):
                cmd_args.extend(["--specified_id", specified_ids])
            if creator_ids := data.get("creator_ids"):
                cmd_args.extend(["--creator_id", creator_ids])

            cmd_args.extend([
                "--get_comment", "true" if data.get("enable_comments") else "false",
                "--get_sub_comment", "true" if data.get("enable_sub_comments") else "false",
                "--headless", "true" if data.get("headless") else "false",
            ])

            cmd = _build_run_cmd(cmd_args)

            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=PROJECT_ROOT,
                text=True,
                bufsize=1
            )
            _set_process(process)

            _append_log("INFO", f"Crawler started: {platform} {crawler_type}")
            if process.stdout:
                threading.Thread(
                    target=_stream_pipe,
                    args=(process.stdout, "INFO"),
                    daemon=True,
                ).start()
            if process.stderr:
                threading.Thread(
                    target=_stream_pipe,
                    args=(process.stderr, "ERROR"),
                    daemon=True,
                ).start()

            def _watch_process(proc):
                exit_code = proc.wait()
                level = "INFO" if exit_code == 0 else "ERROR"
                _append_log(level, f"Crawler exited with code {exit_code}")
                _set_process(None)

            threading.Thread(
                target=_watch_process,
                args=(process,),
                daemon=True,
            ).start()

            return Response({
                "status": "ok",
                "message": "Crawler started successfully"
            })

        except Exception as e:
            return Response(
                {"error": f"Failed to start crawler: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _stop_crawler(self):
        """Stop crawler task"""
        process = _get_process()
        if not process or process.poll() is not None:
            return Response(
                {"error": "No crawler is running"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            process.terminate()
            process.wait(timeout=5)
            _append_log("INFO", "Crawler stopped")
            _set_process(None)

            return Response({
                "status": "ok",
                "message": "Crawler stopped successfully"
            })

        except Exception as e:
            return Response(
                {"error": f"Failed to stop crawler: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_status(self):
        """Get crawler status"""
        process = _get_process()
        is_running = process is not None and process.poll() is None
        state = _get_state()

        return Response({
            "running": is_running,
            "platform": state["platform"],
            "login_type": state["login_type"],
            "crawler_type": state["crawler_type"],
        })

    def _get_logs(self, limit: int):
        """Get recent logs"""
        logs = _get_logs()
        logs = logs[-limit:] if limit > 0 else logs
        return Response({"logs": logs})


# ============== Data Management ==============

def get_file_info(file_path: Path) -> dict:
    """Get file information"""
    stat = file_path.stat()
    record_count = None

    # Try to get record count
    try:
        if file_path.suffix == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    record_count = len(data)
        elif file_path.suffix == ".csv":
            with open(file_path, "r", encoding="utf-8") as f:
                record_count = sum(1 for _ in f) - 1  # Subtract header row
    except Exception:
        pass

    return {
        "name": file_path.name,
        "path": str(file_path.relative_to(DATA_DIR)),
        "size": stat.st_size,
        "modified_at": stat.st_mtime,
        "record_count": record_count,
        "type": file_path.suffix[1:] if file_path.suffix else "unknown"
    }


@api_view(['GET'])
@permission_classes([AllowAny])
def list_data_files(request):
    """Get data file list"""
    if not DATA_DIR.exists():
        return Response({"files": []})

    platform = request.GET.get("platform")
    file_type = request.GET.get("file_type")

    files = []
    supported_extensions = {".json", ".csv", ".xlsx", ".xls"}

    for root, dirs, filenames in os.walk(DATA_DIR):
        root_path = Path(root)
        for filename in filenames:
            file_path = root_path / filename
            if file_path.suffix.lower() not in supported_extensions:
                continue

            # Platform filter
            if platform:
                rel_path = str(file_path.relative_to(DATA_DIR))
                if platform.lower() not in rel_path.lower():
                    continue

            # Type filter
            if file_type and file_path.suffix[1:].lower() != file_type.lower():
                continue

            try:
                files.append(get_file_info(file_path))
            except Exception:
                continue

    # Sort by modification time (newest first)
    files.sort(key=lambda x: x["modified_at"], reverse=True)

    return Response({"files": files})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_file_content(request, file_path: str):
    """Get file content or preview"""
    full_path = DATA_DIR / file_path

    if not full_path.exists():
        return Response(
            {"error": "File not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if not full_path.is_file():
        return Response(
            {"error": "Not a file"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Security check: ensure within DATA_DIR
    try:
        full_path.resolve().relative_to(DATA_DIR.resolve())
    except ValueError:
        return Response(
            {"error": "Access denied"},
            status=status.HTTP_403_FORBIDDEN
        )

    preview = request.GET.get("preview", "true").lower() == "true"
    limit = int(request.GET.get("limit", 100))

    if preview:
        # Return preview data
        try:
            if full_path.suffix == ".json":
                with open(full_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return Response({
                            "data": data[:limit],
                            "total": len(data)
                        })
                    return Response({"data": data, "total": 1})

            elif full_path.suffix == ".csv":
                import csv
                with open(full_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    rows = []
                    for i, row in enumerate(reader):
                        if i >= limit:
                            break
                        rows.append(row)
                    # Re-read to get total count
                    f.seek(0)
                    total = sum(1 for _ in f) - 1
                    return Response({"data": rows, "total": total})

            elif full_path.suffix.lower() in (".xlsx", ".xls"):
                import pandas as pd
                # Read first limit rows
                df = pd.read_excel(full_path, nrows=limit)
                # Get total row count
                df_count = pd.read_excel(full_path, usecols=[0])
                total = len(df_count)
                # Convert to list of dictionaries
                rows = df.where(pd.notnull(df), None).to_dict(orient='records')
                return Response({
                    "data": rows,
                    "total": total,
                    "columns": list(df.columns)
                })
            else:
                return Response(
                    {"error": "Unsupported file type for preview"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except json.JSONDecodeError:
            return Response(
                {"error": "Invalid JSON file"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        # Return file download
        return FileResponse(
            path=full_path,
            filename=full_path.name,
            as_attachment=True
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def download_file(request, file_path: str):
    """Download file"""
    full_path = DATA_DIR / file_path

    if not full_path.exists():
        return Response(
            {"error": "File not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if not full_path.is_file():
        return Response(
            {"error": "Not a file"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Security check
    try:
        full_path.resolve().relative_to(DATA_DIR.resolve())
    except ValueError:
        return Response(
            {"error": "Access denied"},
            status=status.HTTP_403_FORBIDDEN
        )

    return FileResponse(
        path=full_path,
        filename=full_path.name,
        as_attachment=True
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_data_stats(request):
    """Get data statistics"""
    if not DATA_DIR.exists():
        return Response({
            "total_files": 0,
            "total_size": 0,
            "by_platform": {},
            "by_type": {}
        })

    stats = {
        "total_files": 0,
        "total_size": 0,
        "by_platform": {},
        "by_type": {}
    }

    supported_extensions = {".json", ".csv", ".xlsx", ".xls"}

    for root, dirs, filenames in os.walk(DATA_DIR):
        root_path = Path(root)
        for filename in filenames:
            file_path = root_path / filename
            if file_path.suffix.lower() not in supported_extensions:
                continue

            try:
                file_stat = file_path.stat()
                stats["total_files"] += 1
                stats["total_size"] += file_stat.st_size

                # Statistics by type
                file_type = file_path.suffix[1:].lower()
                stats["by_type"][file_type] = stats["by_type"].get(file_type, 0) + 1

                # Statistics by platform (inferred from path)
                rel_path = str(file_path.relative_to(DATA_DIR))
                for platform in ["xhs", "dy", "ks", "bili", "wb", "tieba", "zhihu"]:
                    if platform in rel_path.lower():
                        stats["by_platform"][platform] = stats["by_platform"].get(platform, 0) + 1
                        break
            except Exception:
                continue

    return Response(stats)
