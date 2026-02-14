#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Final sync script to sync all platform data to monitor_feed table"""

import json
import pymysql
import time
import sys
import os
from dotenv import load_dotenv

from api.sentiment_service import analyze_sentiment

env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

DB_NAME = os.environ.get('DB_NAME', 'lxr')
DB_USER = os.environ.get('DB_USER', 'lxr')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'lxr123123')
DB_HOST = os.environ.get('DB_HOST', '39.105.122.26')
DB_PORT = int(os.environ.get('DB_PORT', '3306'))

platform_names = {"xhs": "小红书", "dy": "抖音", "ks": "快手", "bili": "B站", "wb": "微博", "tieba": "贴吧", "zhihu": "知乎"}

def sync_all():
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            charset='utf8mb4'
        )
        cursor = connection.cursor()

        print(f"=== Syncing ALL data to monitor_feed ===\n")

        # Clear and sync all platforms
        platforms = [
            ('xhs', 'xhs_note', 'note_id', 'time', 'nickname', 'note_url', ['title', 'desc']),
            ('dy', 'douyin_aweme', 'aweme_id', 'create_time', 'nickname', 'aweme_url', ['title', 'desc']),
            ('ks', 'kuaishou_video', 'video_id', 'create_time', 'nickname', 'video_url', ['title', 'desc']),
            ('bili', 'bilibili_video', 'video_id', 'create_time', 'nickname', 'video_url', ['title', 'desc']),
            ('wb', 'weibo_note', 'note_id', 'create_time', 'nickname', 'note_url', ['content']),
            ('tieba', 'tieba_note', 'note_id', 'publish_time', 'user_nickname', 'note_url', ['title', 'desc']),
            ('zhihu', 'zhihu_content', 'content_id', 'created_time', 'user_nickname', 'content_url', ['title', 'desc', 'content_text']),
        ]

        for platform, table, id_field, time_field, author_field, url_field, content_fields in platforms:
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            if not cursor.fetchone():
                continue

            select_fields = [
                f"CAST(`{id_field}` AS CHAR) AS content_id",
                f"`{time_field}` AS created_at",
                f"`{author_field}` AS author",
                f"`{url_field}` AS url",
                "COALESCE(source_keyword, '') AS source_keyword",
            ] + [f"`{field}` AS `{field}`" for field in content_fields]

            cursor.execute(f"SELECT {', '.join(select_fields)} FROM {table}")
            columns = [col[0] for col in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

            now_ms = int(time.time() * 1000)
            payload = []
            for row in rows:
                content_parts = []
                for field in content_fields:
                    value = row.get(field)
                    if value is not None and str(value).strip():
                        content_parts.append(str(value))
                content = " ".join(content_parts).strip() or "暂无内容"

                raw_created_at = row.get("created_at")
                created_at = 0
                if raw_created_at is not None:
                    raw_str = str(raw_created_at).strip()
                    if raw_str.isdigit():
                        created_at = int(raw_str)

                sentiment_result = analyze_sentiment(content)
                sentiment = sentiment_result.get("sentiment", "neutral")
                sentiment_score = sentiment_result.get("score", 0)
                sentiment_labels = sentiment_result.get("labels") or {}
                is_sensitive = bool(sentiment_labels.get("sensitive")) or sentiment == "sensitive"

                payload.append((
                    platform,
                    platform_names[platform],
                    row.get("content_id", ""),
                    content,
                    row.get("author") or "",
                    row.get("url") or "",
                    created_at,
                    row.get("source_keyword") or "",
                    now_ms,
                    now_ms,
                    sentiment,
                    sentiment_score,
                    json.dumps(sentiment_labels, ensure_ascii=False),
                    1 if is_sensitive else 0,
                ))

            if not payload:
                print(f"[OK] {platform_names[platform]:8s}:      0 records")
                continue

            cursor.executemany(
                """
                INSERT INTO monitor_feed (
                    platform,
                    platform_name,
                    content_id,
                    content,
                    author,
                    url,
                    created_at,
                    source_keyword,
                    add_ts,
                    last_modify_ts,
                    sentiment,
                    sentiment_score,
                    sentiment_labels,
                    is_sensitive
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    content = VALUES(content),
                    author = VALUES(author),
                    url = VALUES(url),
                    created_at = VALUES(created_at),
                    source_keyword = VALUES(source_keyword),
                    last_modify_ts = VALUES(last_modify_ts),
                    sentiment = VALUES(sentiment),
                    sentiment_score = VALUES(sentiment_score),
                    sentiment_labels = VALUES(sentiment_labels),
                    is_sensitive = VALUES(is_sensitive)
                """,
                payload,
            )
            print(f"[OK] {platform_names[platform]:8s}: {cursor.rowcount:6d} records")

        connection.commit()

        cursor.execute("SELECT COUNT(*) FROM monitor_feed")
        total = cursor.fetchone()[0]
        print(f"\n=== Total: {total} records in monitor_feed ===")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    sync_all()
