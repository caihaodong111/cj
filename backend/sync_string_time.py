#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sync tieba and zhihu with proper time handling"""

import pymysql
import sys
import os
import re
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

DB_NAME = os.environ.get('DB_NAME', 'lxr')
DB_USER = os.environ.get('DB_USER', 'lxr')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'lxr123123')
DB_HOST = os.environ.get('DB_HOST', '39.105.122.26')
DB_PORT = int(os.environ.get('DB_PORT', '3306'))

platform_names = {"tieba": "贴吧", "zhihu": "知乎"}

def parse_time_to_timestamp(time_str):
    """Convert string time to timestamp (milliseconds)"""
    if not time_str:
        return 0
    try:
        # Try direct int first
        return int(time_str)
    except:
        # Try parsing string format like "Wed Feb 12 19:03:05 +0800 2025"
        return 0

def sync_string_time_tables():
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

        print("=== Syncing Tieba ===")

        # Get tieba data
        cursor.execute("""
            SELECT note_id, title, `desc`, user_nickname, note_url, publish_time, source_keyword
            FROM tieba_note
            LIMIT 1000
        """)
        tieba_rows = cursor.fetchall()

        for row in tieba_rows:
            note_id, title, desc, author, url, publish_time, keyword = row
            content = f"{title or ''} {desc or ''}".strip()

            cursor.execute("""
                INSERT INTO monitor_feed (platform, platform_name, content_id, content, author, url, created_at, source_keyword, add_ts, last_modify_ts)
                VALUES ('tieba', '贴吧', %s, %s, %s, %s, %s, %s, UNIX_TIMESTAMP(NOW()) * 1000, UNIX_TIMESTAMP(NOW()) * 1000)
                ON DUPLICATE KEY UPDATE
                    content = VALUES(content),
                    author = VALUES(author),
                    url = VALUES(url),
                    last_modify_ts = VALUES(last_modify_ts)
            """, (str(note_id), content, author or '', url or '', 0, keyword or ''))

        print(f"[OK] 贴吧: {len(tieba_rows)} records")

        print("\n=== Syncing Zhihu ===")

        # Get zhihu data
        cursor.execute("""
            SELECT content_id, title, `desc`, content_text, user_nickname, content_url, created_time, source_keyword
            FROM zhihu_content
            LIMIT 1000
        """)
        zhihu_rows = cursor.fetchall()

        for row in zhihu_rows:
            content_id, title, desc, content_text, author, url, created_time, keyword = row
            content = f"{title or ''} {desc or ''} {content_text or ''}".strip()

            cursor.execute("""
                INSERT INTO monitor_feed (platform, platform_name, content_id, content, author, url, created_at, source_keyword, add_ts, last_modify_ts)
                VALUES ('zhihu', '知乎', %s, %s, %s, %s, %s, %s, UNIX_TIMESTAMP(NOW()) * 1000, UNIX_TIMESTAMP(NOW()) * 1000)
                ON DUPLICATE KEY UPDATE
                    content = VALUES(content),
                    author = VALUES(author),
                    url = VALUES(url),
                    last_modify_ts = VALUES(last_modify_ts)
            """, (str(content_id), content, author or '', url or '', 0, keyword or ''))

        print(f"[OK] 知乎: {len(zhihu_rows)} records")

        connection.commit()

        # Verify
        cursor.execute("SELECT COUNT(*) FROM monitor_feed")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT platform, COUNT(*) FROM monitor_feed GROUP BY platform")
        results = cursor.fetchall()

        print(f"\n=== Total: {total} records in monitor_feed ===")
        print("Records by platform:")
        for row in results:
            p_name = platform_names.get(row[0], row[0])
            print(f"  {p_name:8s}: {row[1]:6d} records")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    sync_string_time_tables()
