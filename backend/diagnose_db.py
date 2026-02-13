#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Diagnostic script to check database tables and data"""

import pymysql
import sys
import os

# Load environment variables
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

DB_NAME = os.environ.get('DB_NAME', 'lxr')
DB_USER = os.environ.get('DB_USER', 'lxr')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'lxr123123')
DB_HOST = os.environ.get('DB_HOST', '39.105.122.26')
DB_PORT = int(os.environ.get('DB_PORT', '3306'))

def check_database():
    """Check database tables and data"""
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

        print(f"=== Connected to database '{DB_NAME}' at {DB_HOST}:{DB_PORT} ===\n")

        # Check if monitor_feed table exists
        cursor.execute("SHOW TABLES LIKE 'monitor_feed'")
        result = cursor.fetchone()

        if result:
            print("[OK] monitor_feed table EXISTS")

            # Get table structure
            cursor.execute("DESCRIBE monitor_feed")
            columns = cursor.fetchall()
            print(f"  Columns: {len(columns)}")
            for col in columns[:5]:  # Show first 5 columns
                print(f"    - {col[0]}: {col[1]}")

            # Count records
            cursor.execute("SELECT COUNT(*) FROM monitor_feed")
            count = cursor.fetchone()[0]
            print(f"  Records: {count}")

            if count > 0:
                cursor.execute("SELECT platform, platform_name, content_id, LEFT(content, 30) as content_preview, created_at FROM monitor_feed ORDER BY created_at DESC LIMIT 5")
                rows = cursor.fetchall()
                print("  Latest records:")
                for row in rows:
                    print(f"    [{row[0]}] {row[1]} - {row[3]}...")
        else:
            print("[ERROR] monitor_feed table DOES NOT EXIST")
            print("\nTo create it, run:")
            print("  cd backend")
            print("  python manage.py migrate media_platform")

        print("\n" + "="*60 + "\n")

        # Check platform tables
        platform_tables = {
            'xhs_note': '小红书',
            'douyin_aweme': '抖音',
            'kuaishou_video': '快手',
            'bilibili_video': 'B站',
            'weibo_note': '微博',
            'tieba_note': '贴吧',
            'zhihu_content': '知乎',
        }

        print("=== Platform Tables Status ===\n")

        for table_name, display_name in platform_tables.items():
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            result = cursor.fetchone()

            if result:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"[OK] {display_name:8s} ({table_name}): {count:6d} records")
            else:
                print(f"[--] {display_name:8s} ({table_name}): Table not found")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"[ERROR] Failed to connect to database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_database()
