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
from datetime import datetime
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.db import connection
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.utils.dateparse import parse_datetime, parse_date
from django.utils import timezone
from django.views import View
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from media_platform.models import (
    XhsNote,
    DouyinAweme,
    KuaishouVideo,
    BilibiliVideo,
    WeiboNote,
    TiebaNote,
    ZhihuContent,
    MonitorFeed,
)
from .models import CookieConfig

# Data directory
DATA_DIR = Path(__file__).parent.parent.parent / "data"
PROJECT_ROOT = settings.BASE_DIR.parent
CRAWLER_ROOT = settings.BASE_DIR / "crawler"

CRAWLER_LOCK = threading.Lock()
CRAWLER_PROCESS = None
CRAWLER_BATCH_RUNNING = False
CRAWLER_BATCH_CANCEL = threading.Event()
CRAWLER_LOGS = deque(maxlen=2000)
CRAWLER_STATE = {
    "platform": "xhs",
    "login_type": "qrcode",
    "crawler_type": "search",
}

PLATFORM_PATH_ALIASES = {
    "xhs": ["xhs"],
    "dy": ["douyin", "dy"],
    "ks": ["kuaishou", "ks"],
    "bili": ["bilibili", "bili"],
    "wb": ["weibo", "wb"],
    "tieba": ["tieba"],
    "zhihu": ["zhihu"],
}

PLATFORM_FEED_CONFIG = {
    "xhs": {
        "model": XhsNote,
        "id_field": "note_id",
        "time_field": "time",
        "content_fields": ["title", "desc"],
        "author_field": "nickname",
    },
    "dy": {
        "model": DouyinAweme,
        "id_field": "aweme_id",
        "time_field": "create_time",
        "content_fields": ["title", "desc"],
        "author_field": "nickname",
    },
    "ks": {
        "model": KuaishouVideo,
        "id_field": "video_id",
        "time_field": "create_time",
        "content_fields": ["title", "desc"],
        "author_field": "nickname",
    },
    "bili": {
        "model": BilibiliVideo,
        "id_field": "video_id",
        "time_field": "create_time",
        "content_fields": ["title", "desc"],
        "author_field": "nickname",
    },
    "wb": {
        "model": WeiboNote,
        "id_field": "note_id",
        "time_field": "create_time",
        "content_fields": ["content"],
        "author_field": "nickname",
    },
    "tieba": {
        "model": TiebaNote,
        "id_field": "note_id",
        "time_field": "publish_time",
        "content_fields": ["title", "desc"],
        "author_field": "user_nickname",
    },
    "zhihu": {
        "model": ZhihuContent,
        "id_field": "content_id",
        "time_field": "created_time",
        "content_fields": ["title", "desc", "content_text"],
        "author_field": "user_nickname",
    },
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


def _is_batch_running():
    with CRAWLER_LOCK:
        return CRAWLER_BATCH_RUNNING


def _set_batch_running(value: bool):
    with CRAWLER_LOCK:
        global CRAWLER_BATCH_RUNNING
        CRAWLER_BATCH_RUNNING = value


def _is_crawler_busy():
    process = _get_process()
    return (process is not None and process.poll() is None) or _is_batch_running()


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


def _to_millis(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        ts = int(value)
        return ts if ts > 1_000_000_000_000 else ts * 1000
    if isinstance(value, datetime):
        return int(value.timestamp() * 1000)
    raw = str(value).strip()
    if not raw:
        return None
    if raw.isdigit():
        ts = int(raw)
        return ts if ts > 1_000_000_000_000 else ts * 1000
    parsed = parse_datetime(raw)
    if parsed is None:
        parsed_date = parse_date(raw)
        if parsed_date:
            parsed = datetime(parsed_date.year, parsed_date.month, parsed_date.day)
    if parsed is None:
        return None
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return int(parsed.timestamp() * 1000)


def _pick_first_value(row: dict, fields):
    for field in fields:
        value = row.get(field)
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


@api_view(['GET'])
@permission_classes([AllowAny])
def get_monitor_feed(request):
    """Get latest feed items from monitor_feed table with pagination support."""
    # 获取分页参数
    try:
        page = max(1, int(request.GET.get("page", 1)))
        page_size = max(1, int(request.GET.get("page_size", 100)))
    except ValueError:
        page = 1
        page_size = 100

    # 计算 offset
    offset = (page - 1) * page_size

    items = []
    total_count = 0
    total_pages = 0

    try:
        # 首先尝试从 monitor_feed 表获取
        # 获取总数
        total_count = MonitorFeed.objects.count()
        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1

        # 获取当前页数据
        queryset = MonitorFeed.objects.order_by("-created_at").values(
            "id", "platform", "platform_name", "content_id", "content", "author", "url", "created_at"
        )[offset:offset + page_size]
        rows = list(queryset)

        for row in rows:
            items.append({
                "id": str(row.get("id")),
                "platform": row.get("platform", ""),
                "platform_name": row.get("platform_name", ""),
                "content_id": row.get("content_id", ""),
                "content": row.get("content") or "",
                "author": row.get("author") or "",
                "url": row.get("url") or "",
                "created_at": row.get("created_at") or 0,
            })

    except Exception as e:
        # 如果 monitor_feed 为空，从平台表获取
        items, total_count, total_pages = _fetch_from_platform_tables_paginated(page, page_size)

    return Response({
        "items": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
        "fetched_at": int(time.time() * 1000),
    })


def _fetch_from_platform_tables(limit: int = None) -> list:
    """Fetch items from platform tables when monitor_feed is empty"""
    items = []
    try:
        # 如果 limit 为 None，则不限制返回数量
        if limit is not None:
            try:
                limit = max(1, int(limit))
            except (TypeError, ValueError):
                limit = 50

        # Fetch from all platform tables and merge
        queries = [
            # xhs
            "SELECT 'xhs' as platform, '小红书' as platform_name, CAST(note_id AS CHAR) as content_id, "
            "CONCAT_WS(' ', IFNULL(`title`, ''), IFNULL(`desc`, '')) as content, nickname as author, "
            "note_url as url, `time` as created_at, COALESCE(source_keyword, '') as source_keyword FROM xhs_note",
            # douyin
            "SELECT 'dy' as platform, '抖音' as platform_name, CAST(aweme_id AS CHAR) as content_id, "
            "CONCAT_WS(' ', IFNULL(`title`, ''), IFNULL(`desc`, '')) as content, nickname as author, "
            "aweme_url as url, create_time as created_at, COALESCE(source_keyword, '') as source_keyword FROM douyin_aweme",
            # bilibili
            "SELECT 'bili' as platform, 'B站' as platform_name, CAST(video_id AS CHAR) as content_id, "
            "CONCAT_WS(' ', IFNULL(`title`, ''), IFNULL(`desc`, '')) as content, nickname as author, "
            "video_url as url, create_time as created_at, COALESCE(source_keyword, '') as source_keyword FROM bilibili_video",
            # weibo
            "SELECT 'wb' as platform, '微博' as platform_name, CAST(note_id AS CHAR) as content_id, "
            "IFNULL(`content`, '') as content, nickname as author, "
            "note_url as url, create_time as created_at, COALESCE(source_keyword, '') as source_keyword FROM weibo_note",
            # tieba
            "SELECT 'tieba' as platform, '贴吧' as platform_name, note_id as content_id, "
            "CONCAT_WS(' ', IFNULL(`title`, ''), IFNULL(`desc`, '')) as content, user_nickname as author, "
            "note_url as url, 0 as created_at, COALESCE(source_keyword, '') as source_keyword FROM tieba_note",
            # zhihu
            "SELECT 'zhihu' as platform, '知乎' as platform_name, content_id as content_id, "
            "CONCAT_WS(' ', IFNULL(`title`, ''), IFNULL(`desc`, ''), IFNULL(`content_text`, '')) as content, user_nickname as author, "
            "content_url as url, 0 as created_at, COALESCE(source_keyword, '') as source_keyword FROM zhihu_content",
        ]

        all_rows = []
        with connection.cursor() as cursor:
            for query in queries:
                # 根据 limit 决定是否添加 LIMIT 子句
                if limit is not None:
                    cursor.execute(f"{query} ORDER BY created_at DESC LIMIT %s", [limit])
                else:
                    cursor.execute(f"{query} ORDER BY created_at DESC")
                columns = [col[0] for col in cursor.description]
                for row in cursor.fetchall():
                    all_rows.append(dict(zip(columns, row)))

        # Sort by created_at descending
        all_rows.sort(key=lambda x: (_to_millis(x.get("created_at")) or 0), reverse=True)

        # 如果 limit 不为 None，则限制返回数量
        rows_to_process = all_rows[:limit] if limit is not None else all_rows

        for row in rows_to_process:
            items.append({
                "id": str(hash(row.get("content_id", ""))),
                "platform": row.get("platform", ""),
                "platform_name": row.get("platform_name", ""),
                "content_id": str(row.get("content_id", "")),
                "content": row.get("content") or "",
                "author": row.get("author") or "",
                "url": row.get("url") or "",
                "created_at": row.get("created_at") or 0,
            })

    except Exception as e:
        items = []

    return items


def _fetch_from_platform_tables_paginated(page: int = 1, page_size: int = 100) -> tuple:
    """Fetch items from platform tables with pagination when monitor_feed is empty"""
    items = []
    total_count = 0
    total_pages = 1

    try:
        # Fetch from all platform tables and merge
        queries = [
            # xhs
            "SELECT 'xhs' as platform, '小红书' as platform_name, CAST(note_id AS CHAR) as content_id, "
            "CONCAT_WS(' ', IFNULL(`title`, ''), IFNULL(`desc`, '')) as content, nickname as author, "
            "note_url as url, `time` as created_at, COALESCE(source_keyword, '') as source_keyword FROM xhs_note",
            # douyin
            "SELECT 'dy' as platform, '抖音' as platform_name, CAST(aweme_id AS CHAR) as content_id, "
            "CONCAT_WS(' ', IFNULL(`title`, ''), IFNULL(`desc`, '')) as content, nickname as author, "
            "aweme_url as url, create_time as created_at, COALESCE(source_keyword, '') as source_keyword FROM douyin_aweme",
            # bilibili
            "SELECT 'bili' as platform, 'B站' as platform_name, CAST(video_id AS CHAR) as content_id, "
            "CONCAT_WS(' ', IFNULL(`title`, ''), IFNULL(`desc`, '')) as content, nickname as author, "
            "video_url as url, create_time as created_at, COALESCE(source_keyword, '') as source_keyword FROM bilibili_video",
            # weibo
            "SELECT 'wb' as platform, '微博' as platform_name, CAST(note_id AS CHAR) as content_id, "
            "IFNULL(`content`, '') as content, nickname as author, "
            "note_url as url, create_time as created_at, COALESCE(source_keyword, '') as source_keyword FROM weibo_note",
            # tieba
            "SELECT 'tieba' as platform, '贴吧' as platform_name, note_id as content_id, "
            "CONCAT_WS(' ', IFNULL(`title`, ''), IFNULL(`desc`, '')) as content, user_nickname as author, "
            "note_url as url, 0 as created_at, COALESCE(source_keyword, '') as source_keyword FROM tieba_note",
            # zhihu
            "SELECT 'zhihu' as platform, '知乎' as platform_name, content_id as content_id, "
            "CONCAT_WS(' ', IFNULL(`title`, ''), IFNULL(`desc`, ''), IFNULL(`content_text`, '')) as content, user_nickname as author, "
            "content_url as url, 0 as created_at, COALESCE(source_keyword, '') as source_keyword FROM zhihu_content",
        ]

        all_rows = []
        with connection.cursor() as cursor:
            for query in queries:
                cursor.execute(f"{query} ORDER BY created_at DESC")
                columns = [col[0] for col in cursor.description]
                for row in cursor.fetchall():
                    all_rows.append(dict(zip(columns, row)))

        # Sort by created_at descending
        all_rows.sort(key=lambda x: (_to_millis(x.get("created_at")) or 0), reverse=True)

        # Calculate pagination
        total_count = len(all_rows)
        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1

        # Get current page data
        offset = (page - 1) * page_size
        rows_to_process = all_rows[offset:offset + page_size]

        for row in rows_to_process:
            items.append({
                "id": str(hash(row.get("content_id", ""))),
                "platform": row.get("platform", ""),
                "platform_name": row.get("platform_name", ""),
                "content_id": str(row.get("content_id", "")),
                "content": row.get("content") or "",
                "author": row.get("author") or "",
                "url": row.get("url") or "",
                "created_at": row.get("created_at") or 0,
            })

    except Exception as e:
        items = []
        total_count = 0
        total_pages = 1

    return items, total_count, total_pages


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
        if _is_crawler_busy():
            return Response(
                {"error": "Crawler is already running"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = request.data
            platform = data.get("platform", "xhs")
            login_type = data.get("login_type", "qrcode")
            crawler_type = data.get("crawler_type", "search")

            platform_list = data.get("platforms") or platform
            if isinstance(platform_list, str):
                platform_list = [p.strip() for p in platform_list.split(",") if p.strip()]
            elif not isinstance(platform_list, list):
                platform_list = [platform_list]

            platform_list = [str(p).lower() for p in platform_list]
            if not platform_list:
                return Response(
                    {"error": "No platforms provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            supported = {"xhs", "dy", "ks", "bili", "wb", "tieba", "zhihu"}
            invalid = [p for p in platform_list if p not in supported]
            if invalid:
                return Response(
                    {"error": f"Invalid platform(s): {', '.join(invalid)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            def _build_cmd_args(target_platform: str):
                cmd_args = [
                    "--platform", target_platform,
                    "--lt", login_type,
                    "--type", crawler_type,
                    "--save_data_path", str(DATA_DIR),
                ]

                if keywords := data.get("keywords"):
                    cmd_args.extend(["--keywords", keywords])
                if save_option := data.get("save_option"):
                    cmd_args.extend(["--save_data_option", save_option])
                if start_page := data.get("start_page"):
                    cmd_args.extend(["--start", str(start_page)])
                cookies = data.get("cookies")
                if not cookies and login_type == "cookie":
                    cookies = CookieConfig.get_active_cookie(target_platform)
                if cookies:
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
                return cmd_args

            if len(platform_list) > 1:
                def _run_batch():
                    _set_batch_running(True)
                    CRAWLER_BATCH_CANCEL.clear()
                    try:
                        _append_log("INFO", f"Batch crawler started: {', '.join(platform_list)}")
                        for item in platform_list:
                            if CRAWLER_BATCH_CANCEL.is_set():
                                _append_log("INFO", "Batch crawler cancelled")
                                break
                            _update_state(item, login_type, crawler_type)
                            cmd = _build_run_cmd(_build_cmd_args(item))
                            process = _start_process(cmd, item, crawler_type)
                            _finalize_process(process)
                    finally:
                        _set_process(None)
                        _set_batch_running(False)

                threading.Thread(target=_run_batch, daemon=True).start()
                return Response({
                    "status": "ok",
                    "message": "Batch crawler started successfully"
                })

            platform = platform_list[0]
            _update_state(platform, login_type, crawler_type)
            cmd = _build_run_cmd(_build_cmd_args(platform))
            process = _start_process(cmd, platform, crawler_type)

            threading.Thread(
                target=_finalize_process,
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
            if _is_batch_running():
                CRAWLER_BATCH_CANCEL.set()
                _append_log("INFO", "Batch crawler stop requested")
                return Response({
                    "status": "ok",
                    "message": "Batch crawler stop requested"
                })
            return Response(
                {"error": "No crawler is running"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if _is_batch_running():
                CRAWLER_BATCH_CANCEL.set()
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
        is_running = (process is not None and process.poll() is None) or _is_batch_running()
        state = _get_state()

        return Response({
            "status": "running" if is_running else "idle",
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


def _start_process(cmd, platform: str, crawler_type: str):
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
    return process


def _finalize_process(process):
    exit_code = process.wait()
    level = "INFO" if exit_code == 0 else "ERROR"
    _append_log(level, f"Crawler exited with code {exit_code}")
    _set_process(None)
    return exit_code


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
                rel_path = str(file_path.relative_to(DATA_DIR)).lower()
                aliases = PLATFORM_PATH_ALIASES.get(platform.lower(), [platform.lower()])
                if not any(alias in rel_path for alias in aliases):
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
                rel_path = str(file_path.relative_to(DATA_DIR)).lower()
                for platform, aliases in PLATFORM_PATH_ALIASES.items():
                    if any(alias in rel_path for alias in aliases):
                        stats["by_platform"][platform] = stats["by_platform"].get(platform, 0) + 1
                        break
            except Exception:
                continue

    return Response(stats)


# ============== Cookie Management ==============


@api_view(['GET'])
@permission_classes([AllowAny])
def list_cookies(request):
    """获取Cookie配置列表"""
    platform = request.GET.get('platform')
    is_active = request.GET.get('is_active')
    is_valid = request.GET.get('is_valid')

    queryset = CookieConfig.objects.all()

    if platform:
        queryset = queryset.filter(platform=platform)
    if is_active is not None:
        queryset = queryset.filter(is_active=is_active.lower() == 'true')
    if is_valid is not None:
        queryset = queryset.filter(is_valid=is_valid.lower() == 'true')

    cookies = []
    for cookie in queryset:
        cookies.append({
            'id': cookie.id,
            'platform': cookie.platform,
            'platform_display': cookie.get_platform_display(),
            'name': cookie.name,
            'cookies': cookie.cookies,
            'is_active': cookie.is_active,
            'is_valid': cookie.is_valid,
            'last_used_at': cookie.last_used_at.isoformat() if cookie.last_used_at else None,
            'last_verified_at': cookie.last_verified_at.isoformat() if cookie.last_verified_at else None,
            'remark': cookie.remark,
            'created_at': cookie.created_at.isoformat() if cookie.created_at else None,
            'updated_at': cookie.updated_at.isoformat() if cookie.updated_at else None,
        })

    return Response({'cookies': cookies})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_cookie(request, cookie_id: int):
    """获取单个Cookie配置详情"""
    try:
        cookie = CookieConfig.objects.get(id=cookie_id)
        return Response({
            'id': cookie.id,
            'platform': cookie.platform,
            'platform_display': cookie.get_platform_display(),
            'name': cookie.name,
            'cookies': cookie.cookies,
            'is_active': cookie.is_active,
            'is_valid': cookie.is_valid,
            'last_used_at': cookie.last_used_at.isoformat() if cookie.last_used_at else None,
            'last_verified_at': cookie.last_verified_at.isoformat() if cookie.last_verified_at else None,
            'remark': cookie.remark,
            'created_at': cookie.created_at.isoformat() if cookie.created_at else None,
            'updated_at': cookie.updated_at.isoformat() if cookie.updated_at else None,
        })
    except CookieConfig.DoesNotExist:
        return Response(
            {'error': 'Cookie配置不存在'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def create_cookie(request):
    """创建新的Cookie配置"""
    from django.core.exceptions import ValidationError

    data = request.data

    # 检查同平台是否已有激活配置
    platform = data.get('platform')
    is_active = data.get('is_active', True)

    if is_active and platform:
        existing = CookieConfig.objects.filter(platform=platform, is_active=True).first()
        if existing:
            # 如果有其他激活配置，先禁用它们
            CookieConfig.objects.filter(platform=platform, is_active=True).update(is_active=False)

    cookie = CookieConfig.objects.create(
        platform=platform,
        name=data.get('name', '默认配置'),
        cookies=data.get('cookies', ''),
        is_active=is_active,
        is_valid=data.get('is_valid', True),
        remark=data.get('remark', ''),
    )

    return Response({
        'id': cookie.id,
        'message': '创建成功'
    }, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'PATCH'])
@permission_classes([AllowAny])
def update_cookie(request, cookie_id: int):
    """更新Cookie配置"""
    try:
        cookie = CookieConfig.objects.get(id=cookie_id)
    except CookieConfig.DoesNotExist:
        return Response(
            {'error': 'Cookie配置不存在'},
            status=status.HTTP_404_NOT_FOUND
        )

    data = request.data

    # 如果设置为激活，禁用同平台其他激活配置
    if data.get('is_active', cookie.is_active) and not cookie.is_active:
        CookieConfig.objects.filter(
            platform=cookie.platform,
            is_active=True
        ).exclude(id=cookie_id).update(is_active=False)

    cookie.platform = data.get('platform', cookie.platform)
    cookie.name = data.get('name', cookie.name)
    cookie.cookies = data.get('cookies', cookie.cookies)
    cookie.is_active = data.get('is_active', cookie.is_active)
    cookie.is_valid = data.get('is_valid', cookie.is_valid)
    cookie.remark = data.get('remark', cookie.remark)
    cookie.save()

    return Response({'message': '更新成功'})


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_cookie(request, cookie_id: int):
    """删除Cookie配置"""
    try:
        cookie = CookieConfig.objects.get(id=cookie_id)
        cookie.delete()
        return Response({'message': '删除成功'})
    except CookieConfig.DoesNotExist:
        return Response(
            {'error': 'Cookie配置不存在'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def toggle_cookie_status(request, cookie_id: int):
    """切换Cookie激活状态"""
    try:
        cookie = CookieConfig.objects.get(id=cookie_id)

        if cookie.is_active:
            cookie.is_active = False
        else:
            # 禁用同平台其他激活配置
            CookieConfig.objects.filter(
                platform=cookie.platform,
                is_active=True
            ).update(is_active=False)
            cookie.is_active = True

        cookie.save()
        return Response({
            'message': '状态切换成功',
            'is_active': cookie.is_active
        })
    except CookieConfig.DoesNotExist:
        return Response(
            {'error': 'Cookie配置不存在'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_active_cookie(request):
    """获取指定平台的激活Cookie（供爬虫使用）"""
    platform = request.GET.get('platform')
    if not platform:
        return Response(
            {'error': '请指定平台'},
            status=status.HTTP_400_BAD_REQUEST
        )

    cookies = CookieConfig.get_active_cookie(platform)

    # 更新最后使用时间
    config = CookieConfig.objects.filter(platform=platform, is_active=True, is_valid=True).first()
    if config:
        from django.utils import timezone
        config.last_used_at = timezone.now()
        config.save(update_fields=['last_used_at'])

    return Response({
        'platform': platform,
        'cookies': cookies,
        'exists': bool(cookies)
    })
