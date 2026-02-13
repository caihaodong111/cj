#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Manual script to sync existing data to monitor_feed table"""

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

# Platform name mapping
PLATFORM_NAMES = {
    "xhs": "小红书",
    "dy": "抖音",
    "ks": "快手",
    "bili": "B站",
    "wb": "微博",
    "tieba": "tieba",
    "zhihu": "知乎",
}

# Platform table configurations
PLATFORM_CONFIGS = {
    'xhs_note': {
        'platform': 'xhs',
        'id_field': 'note_id',
        'time_field': 'time',
        'content_fields': ['title', 'desc'],
        'author_field': 'nickname',
        'url_field': 'note_url',
    },
    'douyin_aweme': {
        'platform': 'dy',
        'id_field': 'aweme_id',
        'time_field': 'create_time',
        'content_fields': ['title', 'desc'],
        'author_field': 'nickname',
        'url_field': 'aweme_url',
    },
    'kuaishou_video': {
        'platform': 'ks',
        'id_field': 'video_id',
        'time_field': 'create_time',
        'content_fields': ['title', 'desc'],
        'author_field': 'nickname',
        'url_field': 'video_url',
    },
    'bilibili_video': {
        'platform': 'bili',
        'id_field': 'video_id',
        'time_field': 'create_time',
        'content_fields': ['title', 'desc'],
        'author_field': 'nickname',
        'url_field': 'video_url',
    },
    'weibo_note': {
        'platform': 'wb',
        'id_field': 'note_id',
        'time_field': 'create_time',
        'content_fields': ['content'],
        'author_field': 'nickname',
        'url_field': 'note_url',
    },
    'tieba_note': {
        'platform': 'tieba',
        'id_field': 'note_id',
        'time_field': 'publish_time',
        'time_field_type': 'string',  # Special handling for string timestamp
        'content_fields': ['title', 'desc'],
        'author_field': 'user_nickname',
        'url_field': 'note_url',
    },
    'zhihu_content': {
        'platform': 'zhihu',
        'id_field': 'content_id',
        'time_field': 'created_time',
        'time_field_type': 'string',  # Special handling for string timestamp
        'content_fields': ['title', 'desc', 'content_text'],
        'author_field': 'user_nickname',
        'url_field': 'content_url',
    },
}


def sync_data_to_monitor_feed():
    """Sync data from platform tables to monitor_feed table"""
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

        print(f"=== Connected to database '{DB_NAME}' ===\n")

        # Clear existing monitor_feed data
        cursor.execute("DELETE FROM monitor_feed")
        print("Cleared existing monitor_feed data\n")

        total_synced = 0

        for table_name, config in PLATFORM_CONFIGS.items():
            platform = config['platform']
            id_field = config['id_field']
            time_field = config['time_field']
            time_field_type = config.get('time_field_type', 'integer')
            content_fields = config['content_fields']
            author_field = config['author_field']
            url_field = config['url_field']

            # Check if table exists
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            if not cursor.fetchone():
                print(f"[SKIP] {table_name} does not exist")
                continue

            # Build content concatenation for SQL (desc is reserved, use backticks)
            content_sql = "CONCAT_WS(' ', " + ", ".join([f"IFNULL(`{field}`, '')" for field in content_fields]) + ")"

            # Handle time field based on type
            if time_field_type == 'string':
                # For string timestamps (tieba, zhihu), we'll use 0 and fix later
                time_sql = "0"
            else:
                time_sql = time_field

            # Query data from platform table
            query = f"""
                INSERT INTO monitor_feed (platform, platform_name, content_id, content, author, url, created_at, source_keyword, add_ts, last_modify_ts)
                SELECT
                    '{platform}' as platform,
                    '{PLATFORM_NAMES[platform]}' as platform_name,
                    CAST({id_field} AS CHAR) as content_id,
                    {content_sql} as content,
                    {author_field} as author,
                    {url_field} as url,
                    {time_sql} as created_at,
                    COALESCE(source_keyword, '') as source_keyword,
                    UNIX_TIMESTAMP(NOW()) * 1000 as add_ts,
                    UNIX_TIMESTAMP(NOW()) * 1000 as last_modify_ts
                FROM {table_name}
                ON DUPLICATE KEY UPDATE
                    content = VALUES(content),
                    author = VALUES(author),
                    url = VALUES(url),
                    created_at = VALUES(created_at),
                    source_keyword = VALUES(source_keyword),
                    last_modify_ts = VALUES(last_modify_ts)
            """

            cursor.execute(query)
            affected = cursor.rowcount
            total_synced += affected
            print(f"[OK] {PLATFORM_NAMES[platform]:8s}: {affected:6d} records synced")

        connection.commit()
        cursor.close()
        connection.close()

        print(f"\n=== Total: {total_synced} records synced to monitor_feed ===")

        # Verify
        print("\n=== Verifying monitor_feed table ===")
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            charset='utf8mb4'
        )
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM monitor_feed")
        count = cursor.fetchone()[0]
        cursor.execute("SELECT platform, COUNT(*) as cnt FROM monitor_feed GROUP BY platform")
        by_platform = cursor.fetchall()

        # Show sample data
        cursor.execute("SELECT platform_name, content, author FROM monitor_feed LIMIT 5")
        samples = cursor.fetchall()

        cursor.close()
        connection.close()

        print(f"Total records in monitor_feed: {count}\n")
        print("Records by platform:")
        for row in by_platform:
            print(f"  {PLATFORM_NAMES.get(row[0], row[0]):8s}: {row[1]:6d} records")

        print("\nSample data:")
        for i, row in enumerate(samples, 1):
            print(f"  {i}. [{row[0]}] {row[1][:60]}... by {row[2] or '匿名'}")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    sync_data_to_monitor_feed()
