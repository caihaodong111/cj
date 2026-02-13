#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sync tieba and zhihu data to monitor_feed table"""

import pymysql
import sys
import os
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

DB_NAME = os.environ.get('DB_NAME', 'lxr')
DB_USER = os.environ.get('DB_USER', 'lxr')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'lxr123123')
DB_HOST = os.environ.get('DB_HOST', '39.105.122.26')
DB_PORT = int(os.environ.get('DB_PORT', '3306'))

def sync_remaining_data():
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

        print(f"=== Syncing remaining data to monitor_feed ===\n")

        # Sync tieba_note
        print("Syncing tieba_note...")
        cursor.execute("""
            INSERT INTO monitor_feed (platform, platform_name, content_id, content, author, url, created_at, source_keyword, add_ts, last_modify_ts)
            SELECT
                'tieba' as platform,
                '贴吧' as platform_name,
                note_id as content_id,
                CONCAT_WS(' ', IFNULL(`title`, ''), IFNULL(`desc`, '')) as content,
                user_nickname as author,
                note_url as url,
                0 as created_at,
                COALESCE(source_keyword, '') as source_keyword,
                UNIX_TIMESTAMP(NOW()) * 1000 as add_ts,
                UNIX_TIMESTAMP(NOW()) * 1000 as last_modify_ts
            FROM tieba_note
            ON DUPLICATE KEY UPDATE
                content = VALUES(content),
                author = VALUES(author),
                url = VALUES(url),
                last_modify_ts = VALUES(last_modify_ts)
        """)
        tieba_count = cursor.rowcount
        print(f"[OK] 贴吧: {tieba_count} records synced")

        # Sync zhihu_content
        print("Syncing zhihu_content...")
        cursor.execute("""
            INSERT INTO monitor_feed (platform, platform_name, content_id, content, author, url, created_at, source_keyword, add_ts, last_modify_ts)
            SELECT
                'zhihu' as platform,
                '知乎' as platform_name,
                content_id as content_id,
                CONCAT_WS(' ', IFNULL(`title`, ''), IFNULL(`desc`, ''), IFNULL(`content_text`, '')) as content,
                user_nickname as author,
                content_url as url,
                0 as created_at,
                COALESCE(source_keyword, '') as source_keyword,
                UNIX_TIMESTAMP(NOW()) * 1000 as add_ts,
                UNIX_TIMESTAMP(NOW()) * 1000 as last_modify_ts
            FROM zhihu_content
            ON DUPLICATE KEY UPDATE
                content = VALUES(content),
                author = VALUES(author),
                url = VALUES(url),
                last_modify_ts = VALUES(last_modify_ts)
        """)
        zhihu_count = cursor.rowcount
        print(f"[OK] 知乎: {zhihu_count} records synced")

        connection.commit()

        # Verify final results
        print("\n=== Final Verification ===")
        cursor.execute("SELECT COUNT(*) FROM monitor_feed")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT platform, COUNT(*) FROM monitor_feed GROUP BY platform")
        results = cursor.fetchall()

        print(f"Total records in monitor_feed: {total}\n")
        print("Records by platform:")
        platform_names = {"xhs": "小红书", "dy": "抖音", "ks": "快手", "bili": "B站", "wb": "微博", "tieba": "贴吧", "zhihu": "知乎"}
        for row in results:
            p_name = platform_names.get(row[0], row[0])
            print(f"  {p_name:8s}: {row[1]:6d} records")

        cursor.close()
        connection.close()

        print(f"\n=== Sync Complete! ===")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    sync_remaining_data()
