# -*- coding: utf-8 -*-
from typing import Dict, Optional

from sqlalchemy import select, func

from api.sentiment_service import analyze_sentiment
from database.db_session import get_session
from database.models import (
    MonitorFeed,
    XhsNote,
    DouyinAweme,
    KuaishouVideo,
    BilibiliVideo,
    WeiboNote,
    TiebaNote,
    ZhihuContent,
)
from tools.time_util import get_current_timestamp


PLATFORM_NAMES = {
    "xhs": "小红书",
    "dy": "抖音",
    "ks": "快手",
    "bili": "B站",
    "wb": "微博",
    "tieba": "贴吧",
    "zhihu": "知乎",
}


def _build_content_text(content_item: Dict) -> str:
    parts = []
    for key in ("title", "desc", "content", "content_text"):
        value = content_item.get(key)
        if value:
            parts.append(str(value))
    content = " ".join(parts).strip()
    if not content:
        content = str(content_item.get("text", "")) or "暂无内容"
    return content


def _get_content_id(content_item: Dict) -> str:
    return str(
        content_item.get("note_id")
        or content_item.get("aweme_id")
        or content_item.get("video_id")
        or content_item.get("content_id")
        or ""
    )


def _get_created_at(content_item: Dict) -> int:
    created_at = (
        content_item.get("time")
        or content_item.get("create_time")
        or content_item.get("created_time")
        or content_item.get("publish_time")
        or 0
    )
    try:
        return int(created_at)
    except (ValueError, TypeError):
        return 0


async def _sync_with_session(session, platform: str, content_item: Dict) -> bool:
    content_id = _get_content_id(content_item)
    if not content_id:
        return False

    content = _build_content_text(content_item)
    ip_location = content_item.get("ip_location")
    author = str(content_item.get("nickname") or content_item.get("user_nickname") or "")
    url = str(
        content_item.get("note_url")
        or content_item.get("aweme_url")
        or content_item.get("video_url")
        or content_item.get("content_url")
        or ""
    )
    created_at = _get_created_at(content_item)

    sentiment_result = analyze_sentiment(content)
    sentiment = sentiment_result.get("sentiment", "neutral")
    sentiment_score = sentiment_result.get("score")
    sentiment_labels = sentiment_result.get("labels") or {}
    is_sensitive = bool(sentiment_labels.get("sensitive")) or sentiment == "sensitive"

    now_ts = int(get_current_timestamp())

    result = await session.execute(
        select(MonitorFeed).where(
            MonitorFeed.platform == platform,
            MonitorFeed.content_id == content_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        if ip_location:
            extra_data = existing.extra_data or {}
            if isinstance(extra_data, dict):
                extra_data["ip_location"] = ip_location
                existing.extra_data = extra_data
        existing.content = content
        existing.author = author
        existing.url = url
        existing.created_at = created_at
        existing.source_keyword = content_item.get("source_keyword", "")
        existing.sentiment = sentiment
        existing.sentiment_score = sentiment_score
        existing.sentiment_labels = sentiment_labels
        existing.is_sensitive = is_sensitive
        existing.last_modify_ts = now_ts
    else:
        extra_data = {"ip_location": ip_location} if ip_location else None
        session.add(
            MonitorFeed(
                platform=platform,
                platform_name=PLATFORM_NAMES.get(platform, platform),
                content_id=content_id,
                content=content,
                author=author,
                url=url,
                created_at=created_at,
                source_keyword=content_item.get("source_keyword", ""),
                extra_data=extra_data,
                sentiment=sentiment,
                sentiment_score=sentiment_score,
                sentiment_labels=sentiment_labels,
                is_sensitive=is_sensitive,
                add_ts=now_ts,
                last_modify_ts=now_ts,
            )
        )
    return True


async def sync_to_monitor_feed(platform: str, content_item: Dict) -> None:
    async with get_session() as session:
        if session is None:
            return
        await _sync_with_session(session, platform, content_item)


async def _get_monitor_feed_cutoff(session, platform: str) -> int:
    result = await session.execute(
        select(
            func.max(
                func.coalesce(
                    MonitorFeed.last_modify_ts,
                    MonitorFeed.add_ts,
                    0,
                )
            )
        ).where(MonitorFeed.platform == platform)
    )
    cutoff = result.scalar()
    return int(cutoff or 0)

def _safe_attr(obj, name: str):
    return getattr(obj, name, None)


def _safe_int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _model_to_content_item(platform: str, record) -> Dict:
    if platform == "xhs":
        return {
            "note_id": _safe_attr(record, "note_id"),
            "title": _safe_attr(record, "title"),
            "desc": _safe_attr(record, "desc"),
            "nickname": _safe_attr(record, "nickname"),
            "note_url": _safe_attr(record, "note_url"),
            "time": _safe_attr(record, "time"),
            "source_keyword": _safe_attr(record, "source_keyword"),
        }
    if platform == "dy":
        return {
            "aweme_id": _safe_attr(record, "aweme_id"),
            "title": _safe_attr(record, "title"),
            "desc": _safe_attr(record, "desc"),
            "nickname": _safe_attr(record, "nickname"),
            "aweme_url": _safe_attr(record, "aweme_url"),
            "create_time": _safe_attr(record, "create_time"),
            "source_keyword": _safe_attr(record, "source_keyword"),
        }
    if platform == "ks":
        return {
            "video_id": _safe_attr(record, "video_id"),
            "title": _safe_attr(record, "title"),
            "desc": _safe_attr(record, "desc"),
            "nickname": _safe_attr(record, "nickname"),
            "video_url": _safe_attr(record, "video_url"),
            "create_time": _safe_attr(record, "create_time"),
            "source_keyword": _safe_attr(record, "source_keyword"),
        }
    if platform == "bili":
        return {
            "video_id": _safe_attr(record, "video_id"),
            "title": _safe_attr(record, "title"),
            "desc": _safe_attr(record, "desc"),
            "nickname": _safe_attr(record, "nickname"),
            "video_url": _safe_attr(record, "video_url"),
            "create_time": _safe_attr(record, "create_time"),
            "source_keyword": _safe_attr(record, "source_keyword"),
        }
    if platform == "wb":
        return {
            "note_id": _safe_attr(record, "note_id"),
            "content": _safe_attr(record, "content"),
            "nickname": _safe_attr(record, "nickname"),
            "note_url": _safe_attr(record, "note_url"),
            "create_time": _safe_attr(record, "create_time"),
            "source_keyword": _safe_attr(record, "source_keyword"),
        }
    if platform == "tieba":
        return {
            "note_id": _safe_attr(record, "note_id"),
            "title": _safe_attr(record, "title"),
            "desc": _safe_attr(record, "desc"),
            "user_nickname": _safe_attr(record, "user_nickname"),
            "note_url": _safe_attr(record, "note_url"),
            "publish_time": _safe_int(_safe_attr(record, "publish_time")),
            "source_keyword": _safe_attr(record, "source_keyword"),
        }
    if platform == "zhihu":
        return {
            "content_id": _safe_attr(record, "content_id"),
            "title": _safe_attr(record, "title"),
            "desc": _safe_attr(record, "desc"),
            "content_text": _safe_attr(record, "content_text"),
            "user_nickname": _safe_attr(record, "user_nickname"),
            "content_url": _safe_attr(record, "content_url"),
            "created_time": _safe_int(_safe_attr(record, "created_time")),
            "source_keyword": _safe_attr(record, "source_keyword"),
        }
    return {}


PLATFORM_MODEL_MAP = {
    "xhs": XhsNote,
    "dy": DouyinAweme,
    "ks": KuaishouVideo,
    "bili": BilibiliVideo,
    "wb": WeiboNote,
    "tieba": TiebaNote,
    "zhihu": ZhihuContent,
}


async def sync_platform_incremental(platform: str, batch_size: int = 500) -> int:
    model = PLATFORM_MODEL_MAP.get(platform)
    if model is None:
        return 0
    synced = 0
    async with get_session() as session:
        if session is None:
            return 0
        cutoff = await _get_monitor_feed_cutoff(session, platform)
        offset = 0
        while True:
            stmt = (
                select(model)
                .where(func.coalesce(model.last_modify_ts, model.add_ts, 0) > cutoff)
                .order_by(func.coalesce(model.last_modify_ts, model.add_ts, 0))
                .limit(batch_size)
                .offset(offset)
            )
            result = await session.execute(stmt)
            rows = result.scalars().all()
            if not rows:
                break
            for row in rows:
                content_item = _model_to_content_item(platform, row)
                if await _sync_with_session(session, platform, content_item):
                    synced += 1
            offset += batch_size
    return synced


async def sync_xhs_notes_incremental(batch_size: int = 500) -> int:
    return await sync_platform_incremental("xhs", batch_size=batch_size)
