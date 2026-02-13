#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Final sync script to sync all platform data to monitor_feed table"""

import pymysql
import sys
import os
from dotenv import load_dotenv

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
            ('bili', 'bilibili_video', 'video_id', 'create_time', 'nickname', 'video_url', ['title', 'desc']),
            ('wb', 'weibo_note', 'note_id', 'create_time', 'nickname', 'note_url', ['content']),
            ('tieba', 'tieba_note', 'note_id', 'publish_time', 'user_nickname', 'note_url', ['title', 'desc']),
            ('zhihu', 'zhihu_content', 'content_id', 'created_time', 'user_nickname', 'content_url', ['title', 'desc', 'content_text']),
        ]

        for platform, table, id_field, time_field, author_field, url_field, content_fields in platforms:
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            if not cursor.fetchone():
                continue

            content_sql = "CONCAT_WS(' ', " + ", ".join([f"IFNULL(`{f}`, '')" for f in content_fields]) + ")"

            cursor.execute(f"""
                INSERT INTO monitor_feed (platform, platform_name, content_id, content, author, url, created_at, source_keyword, add_ts, last_modify_ts)
                SELECT '{platform}', '{platform_names[platform]}', CAST({id_field} AS CHAR),
                    {content_sql}, {author_field}, {url_field}, {time_field},
                    COALESCE(source_keyword, ''), UNIX_TIMESTAMP(NOW()) * 1000, UNIX_TIMESTAMP(NOW()) * 1000
                FROM {table}
                ON DUPLICATE KEY UPDATE
                    content = VALUES(content),
                    author = VALUES(author),
                    url = VALUES(url),
                    last_modify_ts = VALUES(last_modify_ts)
            """)
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
