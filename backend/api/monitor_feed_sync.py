# -*- coding: utf-8 -*-
import os
import django
import logging
from asgiref.sync import sync_to_async

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mediacrawler_config.settings')
django.setup()

from api.sentiment_service import analyze_sentiment
from media_platform.models import MonitorFeed

PLATFORM_NAMES = {
    "xhs": "小红书",
    "dy": "抖音",
    "ks": "快手",
    "bili": "B站",
    "wb": "微博",
    "tieba": "贴吧",
    "zhihu": "知乎",
}


def _sync_to_monitor_feed_sync(platform: str, content_item: dict):
    """同步版本的同步函数，在线程池中执行"""
    try:
        content_id = str(content_item.get("note_id") or content_item.get("aweme_id") or
                          content_item.get("video_id") or content_item.get("content_id") or "")
        if not content_id:
            logger.debug(f"Skipping item without content_id for platform {platform}")
            return

        content_parts = []
        if content_item.get("title"):
            content_parts.append(str(content_item["title"]))
        if content_item.get("desc"):
            content_parts.append(str(content_item["desc"]))
        if content_item.get("content"):
            content_parts.append(str(content_item["content"]))
        if content_item.get("content_text"):
            content_parts.append(str(content_item["content_text"]))

        content = " ".join(content_parts).strip()
        if not content:
            content = str(content_item.get("text", "")) or "暂无内容"

        author = str(content_item.get("nickname") or content_item.get("user_nickname") or "")
        url = str(content_item.get("note_url") or content_item.get("aweme_url") or
                   content_item.get("video_url") or content_item.get("content_url") or "")

        created_at = (
            content_item.get("time")
            or content_item.get("create_time")
            or content_item.get("created_time")
            or content_item.get("publish_time")
            or 0
        )
        try:
            created_at = int(created_at)
        except (ValueError, TypeError):
            created_at = 0

        sentiment_result = analyze_sentiment(content)
        sentiment = sentiment_result.get("sentiment", "neutral")
        sentiment_score = sentiment_result.get("score")
        sentiment_labels = sentiment_result.get("labels") or {}
        is_sensitive = bool(sentiment_labels.get("sensitive")) or sentiment == "sensitive"

        existing = MonitorFeed.objects.filter(platform=platform, content_id=content_id).first()

        if existing:
            existing.content = content
            existing.author = author
            existing.url = url
            existing.created_at = created_at
            existing.source_keyword = content_item.get("source_keyword", "")
            existing.sentiment = sentiment
            existing.sentiment_score = sentiment_score
            existing.sentiment_labels = sentiment_labels
            existing.is_sensitive = is_sensitive
            existing.save()
            logger.debug(f"Updated {platform} item {content_id}")
        else:
            MonitorFeed.objects.create(
                platform=platform,
                platform_name=PLATFORM_NAMES.get(platform, platform),
                content_id=content_id,
                content=content,
                author=author,
                url=url,
                created_at=created_at,
                source_keyword=content_item.get("source_keyword", ""),
                sentiment=sentiment,
                sentiment_score=sentiment_score,
                sentiment_labels=sentiment_labels,
                is_sensitive=is_sensitive,
            )
            logger.info(f"Created {platform} item {content_id}")

    except Exception as e:
        logger.error(f"Failed to sync {platform} item: {e}", exc_info=True)


# 创建同步到异步的包装器
_sync_to_monitor_feed_async = sync_to_async(_sync_to_monitor_feed_sync)


def sync_to_monitor_feed(platform: str, content_item: dict):
    """同步函数，用于同步上下文"""
    _sync_to_monitor_feed_sync(platform, content_item)


async def async_sync_to_monitor_feed(platform: str, content_item: dict):
    """异步函数，用于异步上下文"""
    await _sync_to_monitor_feed_async(platform, content_item)
