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
import logging
import subprocess
import sys
import time
import threading
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Optional

# 创建爬虫日志记录器，输出到 Django 终端
crawler_logger = logging.getLogger("crawler")
crawler_logger.setLevel(logging.INFO)
# 如果 logger 还没有 handler，添加 console handler
if not crawler_logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '[%(levelname)s] %(message)s'
    ))
    crawler_logger.addHandler(console_handler)

from django.conf import settings
from django.db import connection, models
from django.db.models.functions import Coalesce
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.utils.dateparse import parse_datetime, parse_date
from django.utils import timezone
from django.views import View

# 导入情绪分析服务
from api.sentiment_service import analyze_sentiment
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

PLATFORM_NAMES = {
    "xhs": "小红书",
    "dy": "抖音",
    "ks": "快手",
    "bili": "B站",
    "wb": "微博",
    "tieba": "贴吧",
    "zhihu": "知乎",
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

PLATFORM_URL_FIELDS = {
    "xhs": "note_url",
    "dy": "aweme_url",
    "ks": "video_url",
    "bili": "video_url",
    "wb": "note_url",
    "tieba": "note_url",
    "zhihu": "content_url",
}


def _build_run_cmd(args):
    """Build command to run main.py via the current Python executable."""
    return [sys.executable, str(CRAWLER_ROOT / "main.py"), *args]


def _append_log(level: str, message: str):
    """添加日志到内存队列，同时输出到 Django 终端"""
    with CRAWLER_LOCK:
        CRAWLER_LOGS.append({
            "level": level,
            "message": message,
            "timestamp": time.time(),
        })
    # 同时输出到 Django 终端
    log_level = logging.INFO if level == "INFO" else logging.ERROR
    crawler_logger.log(log_level, message)


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
    """流式读取管道输出，同时存储到内存队列和输出到 Django 终端"""
    try:
        for line in iter(pipe.readline, ""):
            if not line:
                break
            message = line.rstrip()
            _append_log(level, message)
            # 同时输出到 Django 终端
            log_level = logging.INFO if level == "INFO" else logging.ERROR
            crawler_logger.log(log_level, message)
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
    """Get latest feed items from monitor_feed table with pagination support.

    优化版本：
    1. 使用数据库聚合计算统计数据，避免全表扫描
    2. 仅对需要的数据进行情绪分析（sentiment_score为None时）
    3. 使用更高效的分页查询
    """
    from django.db.models import Count, Avg, Case, When, IntegerField, F

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

    # ============== 优化1: 使用数据库聚合获取全局统计数据 ==============
    # 一次性获取所有统计信息，避免多次查询
    global_stats = MonitorFeed.objects.aggregate(
        total_count=Count('id'),
        sensitive_count=Count(Case(When(is_sensitive=True, then=1), output_field=IntegerField())),
        positive_count=Count(Case(When(sentiment='positive', then=1), output_field=IntegerField())),
        negative_count=Count(Case(When(sentiment='negative', then=1), output_field=IntegerField())),
        neutral_count=Count(Case(When(sentiment='neutral', then=1), output_field=IntegerField())),
        avg_sentiment_score=Avg('sentiment_score'),
    )

    total_count = global_stats['total_count'] or 0
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1

    # 获取全局情绪分布统计
    sentiment_distribution = {
        "positive": global_stats['positive_count'] or 0,
        "negative": global_stats['negative_count'] or 0,
        "neutral": global_stats['neutral_count'] or 0,
        "sensitive": global_stats['sensitive_count'] or 0,
    }

    # ============== 优化2: 分页查询，只获取当前页数据 ==============
    # 使用 select_related/prefetch_related 如果有外键关系（当前没有）
    # 只查询需要的字段
    queryset = MonitorFeed.objects.order_by("-created_at").values(
        "id",
        "platform",
        "platform_name",
        "content_id",
        "content",
        "author",
        "url",
        "created_at",
        "sentiment",
        "sentiment_score",
        "sentiment_labels",
        "is_sensitive",
    )[offset:offset + page_size]
    rows = list(queryset)

    for row in rows:
        content_text = row.get("content") or ""
        sentiment = row.get("sentiment") or "neutral"
        sentiment_score = row.get("sentiment_score")
        sentiment_labels = row.get("sentiment_labels")
        is_sensitive = row.get("is_sensitive")

        # ============== 优化3: 仅对需要的数据进行情绪分析 ==============
        # 只有当 sentiment_score 为 None 时才进行分析
        if sentiment_score is None:
            sentiment_result = analyze_sentiment(content_text)
            sentiment = sentiment_result.get("sentiment", sentiment)
            sentiment_score = sentiment_result.get("score", 0)
            sentiment_labels = sentiment_result.get("labels", {})

            # 可选：异步更新数据库，下次查询时就不需要再分析了
            try:
                MonitorFeed.objects.filter(id=row.get("id")).update(
                    sentiment=sentiment,
                    sentiment_score=sentiment_score,
                    sentiment_labels=sentiment_labels,
                )
            except Exception:
                pass  # 更新失败不影响返回数据

        if is_sensitive is None:
            is_sensitive = bool(sentiment_labels.get("sensitive")) or sentiment == "sensitive"
        if is_sensitive:
            sentiment = "sensitive"

        items.append({
            "id": str(row.get("id")),
            "platform": row.get("platform", ""),
            "platform_name": row.get("platform_name", ""),
            "content_id": row.get("content_id", ""),
            "content": content_text,
            "author": row.get("author") or "",
            "url": row.get("url") or "",
            "created_at": row.get("created_at") or 0,
            "sentiment": sentiment,
            "sentiment_score": sentiment_score or 0,
            "sentiment_labels": sentiment_labels or {},
            "is_sensitive": bool(is_sensitive),
        })

    # 计算情感指数（使用全局平均值而不是当前页）
    avg_sentiment = global_stats['avg_sentiment_score'] or 0

    # 计算热度（基于数据量和时间）
    hot_score = min(100, (total_count / 10) if total_count > 0 else 0)

    return Response({
        "items": items,
        "stats": {
            "total": total_count,
            "sensitive": sentiment_distribution["sensitive"],
            "sentiment_index": round(avg_sentiment * 10) / 10,  # -1到1，乘10放大
            "hot_score": hot_score,
        },
        "sentiment_distribution": sentiment_distribution,
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


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sensitive_feed(request):
    """Get sensitive feed items from monitor_feed with optional platform filter."""
    platform = request.GET.get("platform")
    sort_by = request.GET.get("sort_by")
    sort_order = request.GET.get("sort_order", "asc").lower()
    try:
        page = max(1, int(request.GET.get("page", 1)))
        page_size = max(1, int(request.GET.get("page_size", 50)))
    except ValueError:
        page = 1
        page_size = 50

    offset = (page - 1) * page_size
    queryset = MonitorFeed.objects.filter(
        models.Q(is_sensitive=True) | models.Q(sentiment="sensitive")
    )
    if platform:
        queryset = queryset.filter(platform=platform)

    latest_update_ts = queryset.aggregate(
        max_ts=models.Max(Coalesce("last_modify_ts", "add_ts", 0))
    ).get("max_ts") or 0

    if sort_by == "sensitive":
        queryset = queryset.annotate(
            sensitive_rank=models.Case(
                models.When(
                    models.Q(is_sensitive=True) | models.Q(sentiment="sensitive"),
                    then=models.Value(0),
                ),
                default=models.Value(1),
                output_field=models.IntegerField(),
            )
        )
        order_field = "sensitive_rank" if sort_order != "desc" else "-sensitive_rank"
        queryset = queryset.order_by(order_field, "-created_at")
    else:
        queryset = queryset.order_by("-created_at")

    total_count = queryset.count()
    if platform and total_count == 0:
        items, total_count, total_pages, latest_update_ts = _fetch_platform_feed_data(
            platform, page, page_size
        )
        return Response({
            "items": items,
            "latest_update_ts": latest_update_ts,
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
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1

    rows = list(
        queryset.values(
            "id",
            "platform",
            "platform_name",
            "content_id",
            "content",
            "author",
            "url",
            "created_at",
            "sentiment",
            "sentiment_score",
            "sentiment_labels",
            "is_sensitive",
            "extra_data",
        )[offset:offset + page_size]
    )

    content_ids_by_platform = {}
    for row in rows:
        platform_key = row.get("platform")
        content_ids_by_platform.setdefault(platform_key, []).append(row.get("content_id"))

    interactions_map_by_platform = {
        platform_key: _get_interactions_from_platform(platform_key, ids)
        for platform_key, ids in content_ids_by_platform.items()
    }

    items = []
    for row in rows:
        extra_data = row.get("extra_data") or {}
        extra_ip = extra_data.get("ip_location") if isinstance(extra_data, dict) else None

        # 获取互动数据，优先使用interactions_map中的ip_location，否则使用extra_ip
        interaction_data = interactions_map_by_platform.get(row.get("platform"), {}).get(row.get("content_id"), {})
        final_ip_location = interaction_data.get("ip_location") or extra_ip or "-"

        items.append({
            "id": str(row.get("id")),
            "platform": row.get("platform", ""),
            "platform_name": row.get("platform_name", ""),
            "content_id": row.get("content_id", ""),
            "content": row.get("content") or "",
            "author": row.get("author") or "",
            "url": row.get("url") or "",
            "created_at": row.get("created_at") or 0,
            "sentiment": row.get("sentiment") or "sensitive",
            "sentiment_score": row.get("sentiment_score") or 0,
            "sentiment_labels": row.get("sentiment_labels") or {},
            "is_sensitive": True,
            "ip_location": final_ip_location,
            **{k: v for k, v in interaction_data.items() if k != "ip_location"},
        })

    return Response({
        "items": items,
        "latest_update_ts": latest_update_ts,
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


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_feed(request):
    """Get all feed items from monitor_feed with optional platform filter."""
    platform = request.GET.get("platform")
    sort_by = request.GET.get("sort_by")
    sort_order = request.GET.get("sort_order", "asc").lower()
    try:
        page = max(1, int(request.GET.get("page", 1)))
        page_size = max(1, int(request.GET.get("page_size", 50)))
    except ValueError:
        page = 1
        page_size = 50

    offset = (page - 1) * page_size
    queryset = MonitorFeed.objects.all()
    if platform:
        queryset = queryset.filter(platform=platform)

    latest_update_ts = queryset.aggregate(
        max_ts=models.Max(Coalesce("last_modify_ts", "add_ts", 0))
    ).get("max_ts") or 0

    if sort_by == "sensitive":
        queryset = queryset.annotate(
            sensitive_rank=models.Case(
                models.When(
                    models.Q(is_sensitive=True) | models.Q(sentiment="sensitive"),
                    then=models.Value(0),
                ),
                default=models.Value(1),
                output_field=models.IntegerField(),
            )
        )
        order_field = "sensitive_rank" if sort_order != "desc" else "-sensitive_rank"
        queryset = queryset.order_by(order_field, "-created_at")
    else:
        queryset = queryset.order_by("-created_at")

    total_count = queryset.count()
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1

    rows = list(
        queryset.values(
            "id",
            "platform",
            "platform_name",
            "content_id",
            "content",
            "author",
            "url",
            "created_at",
            "sentiment",
            "sentiment_score",
            "sentiment_labels",
            "is_sensitive",
            "extra_data",
        )[offset:offset + page_size]
    )

    content_ids_by_platform = {}
    for row in rows:
        platform_key = row.get("platform")
        content_ids_by_platform.setdefault(platform_key, []).append(row.get("content_id"))

    interactions_map_by_platform = {
        platform_key: _get_interactions_from_platform(platform_key, ids)
        for platform_key, ids in content_ids_by_platform.items()
    }

    items = []
    for row in rows:
        is_sensitive = row.get("is_sensitive")
        sentiment = row.get("sentiment") or "neutral"
        sentiment_labels = row.get("sentiment_labels") or {}
        extra_data = row.get("extra_data") or {}
        extra_ip = extra_data.get("ip_location") if isinstance(extra_data, dict) else None

        # 确保敏感状态正确设置
        if is_sensitive is None:
            is_sensitive = bool(sentiment_labels.get("sensitive")) or sentiment == "sensitive"

        # 获取互动数据，优先使用interactions_map中的ip_location，否则使用extra_ip
        interaction_data = interactions_map_by_platform.get(row.get("platform"), {}).get(row.get("content_id"), {})
        final_ip_location = interaction_data.get("ip_location") or extra_ip or "-"

        items.append({
            "id": str(row.get("id")),
            "platform": row.get("platform", ""),
            "platform_name": row.get("platform_name", ""),
            "content_id": row.get("content_id", ""),
            "content": row.get("content") or "",
            "author": row.get("author") or "",
            "url": row.get("url") or "",
            "created_at": row.get("created_at") or 0,
            "sentiment": sentiment,
            "sentiment_score": row.get("sentiment_score") or 0,
            "sentiment_labels": sentiment_labels,
            "is_sensitive": bool(is_sensitive),
            "ip_location": final_ip_location,
            **{k: v for k, v in interaction_data.items() if k != "ip_location"},
        })

    return Response({
        "items": items,
        "latest_update_ts": latest_update_ts,
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
            # kuaishou
            "SELECT 'ks' as platform, '快手' as platform_name, video_id as content_id, "
            "CONCAT_WS(' ', IFNULL(`title`, ''), IFNULL(`desc`, '')) as content, nickname as author, "
            "video_url as url, create_time as created_at, COALESCE(source_keyword, '') as source_keyword FROM kuaishou_video",
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
            # kuaishou
            "SELECT 'ks' as platform, '快手' as platform_name, video_id as content_id, "
            "CONCAT_WS(' ', IFNULL(`title`, ''), IFNULL(`desc`, '')) as content, nickname as author, "
            "video_url as url, create_time as created_at, COALESCE(source_keyword, '') as source_keyword FROM kuaishou_video",
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
            {"value": "xhs", "label": "小红书", "icon": "book-open"},
            {"value": "dy", "label": "抖音", "icon": "music"},
            {"value": "ks", "label": "快手", "icon": "video"},
            {"value": "bili", "label": "哔哩哔哩", "icon": "tv"},
            {"value": "wb", "label": "微博", "icon": "message-circle"},
            {"value": "tieba", "label": "百度贴吧", "icon": "messages-square"},
            {"value": "zhihu", "label": "知乎", "icon": "help-circle"},
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


def _get_db_preview_row(platform: str, obj) -> dict:
    from media_platform.models import MonitorFeed

    config = PLATFORM_FEED_CONFIG.get(platform, {})
    content_fields = config.get("content_fields", [])
    time_field = config.get("time_field")
    author_field = config.get("author_field")
    id_field = config.get("id_field")

    content_parts = []
    for field in content_fields:
        val = getattr(obj, field, None)
        if val:
            content_parts.append(str(val))
    content = " ".join(content_parts).strip()
    time_value = getattr(obj, time_field, None) if time_field else None

    # Get sentiment and is_sensitive from platform table first
    sentiment = getattr(obj, "sentiment", None)
    is_sensitive = getattr(obj, "is_sensitive", None)

    # Try to get fresh data from MonitorFeed (more up-to-date)
    content_id = getattr(obj, id_field, None) if id_field else None
    if content_id:
        try:
            monitor_feed = MonitorFeed.objects.filter(
                platform=platform,
                content_id=str(content_id)
            ).first()
            if monitor_feed:
                # Use MonitorFeed values if they exist
                sentiment = monitor_feed.sentiment
                is_sensitive = monitor_feed.is_sensitive
        except Exception:
            pass

    return {
        "create_time": time_value,
        "created_time": time_value,
        "content": content,
        "desc": getattr(obj, "desc", None),
        "title": getattr(obj, "title", None),
        "nickname": getattr(obj, author_field, None) if author_field else None,
        "avatar": (
            getattr(obj, "user_avatar", None)
            or getattr(obj, "avatar", None)
            or getattr(obj, "avatar_url", None)
        ),
        "ip_location": getattr(obj, "ip_location", None),
        "sentiment": sentiment,
        "is_sensitive": is_sensitive,
    }


def _get_db_preview_data(platform: str, limit: int) -> tuple[list, int]:
    config = PLATFORM_FEED_CONFIG.get(platform)
    if not config:
        return [], 0

    model = config["model"]
    time_field = config.get("time_field")

    try:
        queryset = model.objects.all()
        if time_field:
            queryset = queryset.order_by(f"-{time_field}")
        else:
            queryset = queryset.order_by("-id")
        total = queryset.count()
        rows = [_get_db_preview_row(platform, obj) for obj in queryset[:limit]]
        return rows, total
    except Exception:
        return [], 0


def _get_monitor_feed_data(platform: str, limit: int = 100, page: int = 1) -> tuple[list, int]:
    """Get data from MonitorFeed table for the given platform"""
    from media_platform.models import MonitorFeed

    if not platform:
        return [], 0

    try:
        offset = (page - 1) * limit
        queryset = MonitorFeed.objects.filter(platform=platform).order_by("-created_at")
        total = queryset.count()

        # Get interactions data from original platform tables
        content_ids_to_fetch = []
        for feed in queryset[offset:offset + limit]:
            content_ids_to_fetch.append(feed.content_id)

        interactions_map = _get_interactions_from_platform(platform, content_ids_to_fetch)

        rows = []
        for feed in queryset[offset:offset + limit]:
            row_data = {
                "create_time": feed.created_at,
                "created_time": feed.created_at,
                "content": feed.content,
                "desc": None,
                "title": None,
                "nickname": feed.author,
                "avatar": None,
                "ip_location": None,
                "sentiment": feed.sentiment,
                "is_sensitive": feed.is_sensitive,
                # Extra fields from MonitorFeed
                "content_id": feed.content_id,
                "platform": feed.platform,
                "platform_name": feed.platform_name,
                "url": feed.url,
            }

            # Add interactions data
            interactions = interactions_map.get(feed.content_id, {})
            row_data.update(interactions)

            rows.append(row_data)
        return rows, total
    except Exception as e:
        import traceback
        traceback.print_exc()
        return [], 0


def _fetch_platform_feed_data(platform: str, page: int, page_size: int) -> tuple[list, int, int, int]:
    config = PLATFORM_FEED_CONFIG.get(platform)
    if not config:
        return [], 0, 1, 0

    model = config["model"]
    id_field = config.get("id_field")
    time_field = config.get("time_field")
    content_fields = config.get("content_fields", [])
    author_field = config.get("author_field")
    url_field = PLATFORM_URL_FIELDS.get(platform)

    try:
        queryset = model.objects.all()
        if time_field:
            queryset = queryset.order_by(f"-{time_field}")
        else:
            queryset = queryset.order_by("-id")

        latest_update_ts = queryset.aggregate(
            max_ts=models.Max(Coalesce("last_modify_ts", "add_ts", 0))
        ).get("max_ts") or 0

        total_count = queryset.count()
        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1

        offset = (page - 1) * page_size
        rows = list(queryset[offset:offset + page_size])

        content_ids = []
        for obj in rows:
            content_id = getattr(obj, id_field, None) if id_field else None
            if content_id is not None:
                content_ids.append(str(content_id))

        interactions_map = _get_interactions_from_platform(platform, content_ids)

        items = []
        for obj in rows:
            content_parts = []
            for field in content_fields:
                val = getattr(obj, field, None)
                if val:
                    content_parts.append(str(val))
            content = " ".join(content_parts).strip()

            content_id = getattr(obj, id_field, None) if id_field else None
            content_id_str = str(content_id) if content_id is not None else ""
            created_at = getattr(obj, time_field, None) if time_field else 0
            author = getattr(obj, author_field, None) if author_field else None
            url = getattr(obj, url_field, None) if url_field else None

            sentiment = getattr(obj, "sentiment", None) or "neutral"
            is_sensitive = getattr(obj, "is_sensitive", None)
            if is_sensitive is None:
                is_sensitive = sentiment == "sensitive"

            interaction_data = interactions_map.get(content_id_str, {})
            final_ip_location = interaction_data.get("ip_location") or getattr(obj, "ip_location", None) or "-"

            items.append({
                "id": str(getattr(obj, "id", "")),
                "platform": platform,
                "platform_name": PLATFORM_NAMES.get(platform, platform),
                "content_id": content_id_str,
                "content": content,
                "author": author or "",
                "url": url or "",
                "created_at": created_at or 0,
                "sentiment": sentiment,
                "sentiment_score": None,
                "sentiment_labels": {},
                "is_sensitive": bool(is_sensitive),
                "ip_location": final_ip_location,
                **{k: v for k, v in interaction_data.items() if k != "ip_location"},
            })

        return items, total_count, total_pages, latest_update_ts
    except Exception:
        return [], 0, 1, 0


def _get_interactions_from_platform(platform: str, content_ids: list) -> dict:
    """Get interactions and ip_location data from original platform tables"""
    if not content_ids:
        return {}

    interactions_map = {}

    try:
        if platform == "xhs":
            from media_platform.models import XhsNote
            notes = XhsNote.objects.filter(note_id__in=content_ids)
            for note in notes:
                interactions_map[note.note_id] = {
                    "ip_location": note.ip_location,
                    "liked_count": _safe_int(note.liked_count),
                    "comment_count": _safe_int(note.comment_count),
                    "share_count": _safe_int(note.share_count),
                    "collected_count": _safe_int(note.collected_count),
                }

        elif platform == "dy":
            from media_platform.models import DouyinAweme
            # Convert string IDs to integers for query
            int_ids = []
            for cid in content_ids:
                try:
                    int_ids.append(int(cid))
                except (ValueError, TypeError):
                    pass
            awemes = DouyinAweme.objects.filter(aweme_id__in=int_ids)
            for aweme in awemes:
                interactions_map[str(aweme.aweme_id)] = {
                    "ip_location": aweme.ip_location,
                    "liked_count": _safe_int(aweme.liked_count),
                    "comment_count": _safe_int(aweme.comment_count),
                    "share_count": _safe_int(aweme.share_count),
                    "collected_count": _safe_int(aweme.collected_count),
                }

        elif platform == "bili":
            from media_platform.models import BilibiliVideo
            int_ids = []
            for cid in content_ids:
                try:
                    int_ids.append(int(cid))
                except (ValueError, TypeError):
                    pass
            videos = BilibiliVideo.objects.filter(video_id__in=int_ids)
            for video in videos:
                interactions_map[str(video.video_id)] = {
                    "ip_location": video.ip_location or None,
                    "liked_count": _safe_int(video.liked_count),
                    "comment_count": _safe_int(video.video_comment),
                    "share_count": _safe_int(video.video_share_count),
                    "collected_count": _safe_int(video.video_favorite_count),
                }

        elif platform == "wb":
            from media_platform.models import WeiboNote
            int_ids = []
            for cid in content_ids:
                try:
                    int_ids.append(int(cid))
                except (ValueError, TypeError):
                    pass
            notes = WeiboNote.objects.filter(note_id__in=int_ids)
            for note in notes:
                interactions_map[str(note.note_id)] = {
                    "ip_location": note.ip_location,
                    "liked_count": _safe_int(note.liked_count),
                    "comment_count": _safe_int(note.comments_count),
                    "share_count": _safe_int(note.shared_count),
                    "collected_count": "0",
                }

        elif platform == "ks":
            from media_platform.models import KuaishouVideo
            videos = KuaishouVideo.objects.filter(video_id__in=content_ids)
            for video in videos:
                interactions_map[video.video_id] = {
                    "ip_location": video.ip_location or None,
                    "liked_count": _safe_int(video.liked_count),
                    "comment_count": "0",
                    "share_count": "0",
                    "collected_count": "0",
                }

        elif platform == "zhihu":
            from media_platform.models import ZhihuContent
            contents = ZhihuContent.objects.filter(content_id__in=content_ids)
            for content in contents:
                interactions_map[content.content_id] = {
                    "ip_location": content.ip_location or None,
                    "liked_count": _safe_int(content.voteup_count),
                    "comment_count": _safe_int(content.comment_count),
                    "share_count": "0",
                    "collected_count": "0",
                }

        elif platform == "tieba":
            from media_platform.models import TiebaNote
            notes = TiebaNote.objects.filter(note_id__in=content_ids)
            for note in notes:
                interactions_map[note.note_id] = {
                    "ip_location": note.ip_location,
                    "liked_count": "0",
                    "comment_count": _safe_int(note.total_replay_num),
                    "share_count": "0",
                    "collected_count": "0",
                }

    except Exception as e:
        import traceback
        traceback.print_exc()

    return interactions_map


def _safe_int(value):
    """Safely convert value to integer string"""
    if value is None or value == "":
        return "0"

    # Handle Chinese number format (e.g., "7.9万", "1.2K")
    if isinstance(value, str):
        value = value.strip()
        # Handle "万" (ten thousand)
        if "万" in value:
            try:
                num_part = value.replace("万", "").strip()
                num = float(num_part) * 10000
                return str(int(num))
            except (ValueError, TypeError):
                pass
        # Handle "K" (thousand)
        elif "K" in value.upper():
            try:
                num_part = value.upper().replace("K", "").strip()
                num = float(num_part) * 1000
                return str(int(num))
            except (ValueError, TypeError):
                pass
        # Handle "w" (ten thousand, lowercase variant)
        elif "w" in value.lower():
            try:
                num_part = value.lower().replace("w", "").strip()
                num = float(num_part) * 10000
                return str(int(num))
            except (ValueError, TypeError):
                pass

    try:
        # If already an int or valid string int
        return str(int(value))
    except (ValueError, TypeError):
        return "0"


def _detect_platform_from_path(file_path: str) -> str:
    """Detect platform from file path"""
    path_lower = file_path.lower()
    for platform, aliases in PLATFORM_PATH_ALIASES.items():
        if any(alias in path_lower for alias in aliases):
            return platform
    return None


def _get_sensitive_map_from_monitor_feed(platform: str, rows: list) -> dict:
    """Get sensitive data map from MonitorFeed table for given rows"""
    from media_platform.models import MonitorFeed

    if not platform or not rows:
        return {}

    # Extract content_ids from rows
    content_ids = []
    for row in rows:
        content_id = _extract_content_id(row, platform)
        if content_id:
            content_ids.append(content_id)

    if not content_ids:
        return {}

    try:
        # Query MonitorFeed for these content_ids
        feeds = MonitorFeed.objects.filter(
            platform=platform,
            content_id__in=content_ids
        ).values("content_id", "sentiment", "is_sensitive")

        return {f["content_id"]: f for f in feeds}
    except Exception:
        return {}


def _extract_content_id(row: dict, platform: str) -> str:
    """Extract content_id from row based on platform"""
    if not row:
        return None

    # Common field names for content_id
    id_fields = ["note_id", "aweme_id", "video_id", "content_id"]

    for field in id_fields:
        val = row.get(field)
        if val:
            return str(val)

    return None


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
    """Get data file list - now returns MonitorFeed platform data as virtual files"""
    from media_platform.models import MonitorFeed

    platform = request.GET.get("platform")
    file_type = request.GET.get("file_type")

    files = []
    supported_extensions = {".json", ".csv", ".xlsx", ".xls"}

    # If platform is specified, check MonitorFeed first
    if platform:
        platform_count = MonitorFeed.objects.filter(platform=platform).count()
        if platform_count > 0:
            platform_name_map = {
                "xhs": "小红书",
                "dy": "抖音",
                "ks": "快手",
                "bili": "B站",
                "wb": "微博",
                "tieba": "贴吧",
                "zhihu": "知乎",
            }
            files.append({
                "name": f"{platform_name_map.get(platform, platform.upper())} 数据",
                "path": f"db/{platform}/contents",
                "size": 0,
                "modified_at": time.time(),
                "record_count": platform_count,
                "type": "db",
            })

    # Also include actual files if needed (optional, can be removed)
    if not platform or not file_type:
        if DATA_DIR.exists():
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
    if file_path.startswith("db/"):
        parts = Path(file_path).parts
        if len(parts) < 2:
            return Response({"error": "Invalid db path"}, status=status.HTTP_400_BAD_REQUEST)
        platform = parts[1].lower()
        preview = request.GET.get("preview", "true").lower() == "true"
        limit = int(request.GET.get("limit", 100))
        page = int(request.GET.get("page", 1))
        if not preview:
            return Response({"error": "DB content does not support download"}, status=status.HTTP_400_BAD_REQUEST)
        # Use MonitorFeed instead of platform table
        rows, total = _get_monitor_feed_data(platform, limit=limit, page=page)
        if total == 0:
            return Response({"data": [], "total": 0})
        return Response({"data": rows, "total": total})

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

    # Check if this is a platform file - if so, return MonitorFeed data instead
    platform = _detect_platform_from_path(file_path)
    if platform and preview:
        page = int(request.GET.get("page", 1))
        rows, total = _get_monitor_feed_data(platform, limit=limit, page=page)
        return Response({"data": rows, "total": total})

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
    stats = {
        "total_files": 0,
        "total_size": 0,
        "by_platform": {},
        "by_type": {}
    }

    supported_extensions = {".json", ".csv", ".xlsx", ".xls"}

    if DATA_DIR.exists():
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

    for platform, config_item in PLATFORM_FEED_CONFIG.items():
        if stats["by_platform"].get(platform, 0) > 0:
            continue
        try:
            db_count = config_item["model"].objects.count()
        except Exception:
            db_count = 0
        if db_count > 0:
            stats["by_platform"][platform] = db_count

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


@api_view(['GET'])
@permission_classes([AllowAny])
def get_platform_sentiment_stats(request):
    """获取各平台的情绪统计数据（用于饼图展示）"""
    from django.db.models import Count

    stats = {
        "xhs": {"positive": 0, "negative": 0, "neutral": 0, "sensitive": 0, "total": 0},
        "dy": {"positive": 0, "negative": 0, "neutral": 0, "sensitive": 0, "total": 0},
        "ks": {"positive": 0, "negative": 0, "neutral": 0, "sensitive": 0, "total": 0},
        "bili": {"positive": 0, "negative": 0, "neutral": 0, "sensitive": 0, "total": 0},
        "wb": {"positive": 0, "negative": 0, "neutral": 0, "sensitive": 0, "total": 0},
        "tieba": {"positive": 0, "negative": 0, "neutral": 0, "sensitive": 0, "total": 0},
        "zhihu": {"positive": 0, "negative": 0, "neutral": 0, "sensitive": 0, "total": 0},
    }

    try:
        queryset = MonitorFeed.objects.values("platform", "sentiment", "is_sensitive").annotate(cnt=Count("id"))
        for row in queryset:
            platform = row.get("platform")
            if platform not in stats:
                continue
            sentiment = row.get("sentiment") or "neutral"
            is_sensitive = bool(row.get("is_sensitive"))
            key = "sensitive" if is_sensitive or sentiment == "sensitive" else sentiment
            if key not in stats[platform]:
                key = "neutral"
            stats[platform][key] += row.get("cnt", 0)
            stats[platform]["total"] += row.get("cnt", 0)
    except Exception:
        pass

    return Response(stats)
