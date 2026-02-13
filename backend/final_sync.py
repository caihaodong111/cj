#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Final complete sync script"""

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

def final_sync():
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

        print(f"=== Final Complete Sync ===\n")

        # Clear all existing data
        cursor.execute("DELETE FROM monitor_feed")
        print("Cleared monitor_feed table")

        total = 0

        # 1. xhs (小红书)
        cursor.execute("""
            INSERT INTO monitor_feed (platform, platform_name, content_id, content, author, url, created_at, source_keyword, add_ts, last_modify_ts)
            SELECT 'xhs', '小红书', CAST(note_id AS CHAR),
                CONCAT_WS(' ', IFNULL(`title`, ''), IFNULL(`desc`, '')),
                nickname, note_url, `time`,
                COALESCE(source_keyword, ''), UNIX_TIMESTAMP(NOW()) * 1000, UNIX_TIMESTAMP(NOW()) * 1000
            FROM xhs_note
        """)
        count = cursor.rowcount
        total += count
        print(f"[OK] 小红书: {count} records")

        # 2. douyin (抖音)
        cursor.execute("""
            INSERT INTO monitor_feed (platform, platform_name, content_id, content, author, url, created_at, source_keyword, add_ts, last_modify_ts)
            SELECT 'dy', '抖音', CAST(aweme_id AS CHAR),
                CONCAT_WS(' ', IFNULL(`title`, ''), IFNULL(`desc`, '')),
                nickname, aweme_url, create_time,
                COALESCE(source_keyword, ''), UNIX_TIMESTAMP(NOW()) * 1000, UNIX_TIMESTAMP(NOW()) * 1000
            FROM douyin_aweme
        """)
        count = cursor.rowcount
        total += count
        print(f"[OK] 抖音: {count} records")

        # 3. bilibili (B站)
        cursor.execute("""
            INSERT INTO monitor_feed (platform, platform_name, content_id, content, author, url, created_at, source_keyword, add_ts, last_modify_ts)
            SELECT 'bili', 'B站', CAST(video_id AS CHAR),
                CONCAT_WS(' ', IFNULL(`title`, ''), IFNULL(`desc`, '')),
                nickname, video_url, create_time,
                COALESCE(source_keyword, ''), UNIX_TIMESTAMP(NOW()) * 1000, UNIX_TIMESTAMP(NOW()) * 1000
            FROM bilibili_video
        """)
        count = cursor.rowcount
        total += count
        print(f"[OK] B站: {count} records")

        # 4. weibo (微博)
        cursor.execute("""
            INSERT INTO monitor_feed (platform, platform_name, content_id, content, author, url, created_at, source_keyword, add_ts, last_modify_ts)
            SELECT 'wb', '微博', CAST(note_id AS CHAR),
                IFNULL(`content`, ''), nickname, note_url, create_time,
                COALESCE(source_keyword, ''), UNIX_TIMESTAMP(NOW()) * 1000, UNIX_TIMESTAMP(NOW()) * 1000
            FROM weibo_note
        """)
        count = cursor.rowcount
        total += count
        print(f"[OK] 微博: {count} records")

        # 5. tieba (贴吧) - use 0 for created_at since it's a string
        cursor.execute("""
            INSERT INTO monitor_feed (platform, platform_name, content_id, content, author, url, created_at, source_keyword, add_ts, last_modify_ts)
            SELECT 'tieba', '贴吧', note_id,
                CONCAT_WS(' ', IFNULL(`title`, ''), IFNULL(`desc`, '')),
                user_nickname, note_url, 0,
                COALESCE(source_keyword, ''), UNIX_TIMESTAMP(NOW()) * 1000, UNIX_TIMESTAMP(NOW()) * 1000
            FROM tieba_note
        """)
        count = cursor.rowcount
        total += count
        print(f"[OK] 贴吧: {count} records")

        # 6. zhihu (知乎) - use 0 for created_at since it's a string
        cursor.execute("""
            INSERT INTO monitor_feed (platform, platform_name, content_id, content, author, url, created_at, source_keyword, add_ts, last_modify_ts)
            SELECT 'zhihu', '知乎', content_id,
                CONCAT_WS(' ', IFNULL(`title`, ''), IFNULL(`desc`, ''), IFNULL(`content_text`, '')),
                user_nickname, content_url, 0,
                COALESCE(source_keyword, ''), UNIX_TIMESTAMP(NOW()) * 1000, UNIX_TIMESTAMP(NOW()) * 1000
            FROM zhihu_content
        """)
        count = cursor.rowcount
        total += count
        print(f"[OK] 知乎: {count} records")

        connection.commit()

        print(f"\n=== Total: {total} records synced ===")

        # Final verification
        cursor.execute("SELECT COUNT(*) FROM monitor_feed")
        final_count = cursor.fetchone()[0]

        cursor.execute("SELECT platform, platform_name, COUNT(*) as cnt FROM monitor_feed GROUP BY platform ORDER BY platform")
        results = cursor.fetchall()

        print(f"\nFinal count: {final_count}\n")
        print("Records by platform:")
        for row in results:
            print(f"  {row[1]:8s}: {row[2]:6d} records")

        # Show sample
        cursor.execute("SELECT platform_name, LEFT(content, 50) as content, author FROM monitor_feed ORDER BY id DESC LIMIT 5")
        samples = cursor.fetchall()
        print("\nLatest 5 records:")
        for i, row in enumerate(samples, 1):
            print(f"  {i}. [{row[0]}] {row[1]}... by {row[2] or '匿名'}")

        cursor.close()
        connection.close()

        print("\n=== Sync Complete! ===")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    final_sync()
