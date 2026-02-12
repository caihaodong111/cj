#!/usr/bin/env python3
"""查看数据库中的爬取数据"""
import pymysql

DB_CONFIG = {
    'host': '39.105.122.26',
    'port': 3306,
    'user': 'lxr',
    'password': 'lxr123123',
    'database': 'lxr'
}

def check_data():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("=" * 50)
        print("小红书数据统计")
        print("=" * 50)

        # 检查表是否存在
        cursor.execute('SHOW TABLES LIKE "xhs_%"')
        tables = [t[0] for t in cursor.fetchall()]

        if not tables:
            print("\n⚠️ 没有找到小红书相关表，请先运行爬虫！")
            return

        # 统计各表数据量
        for table in ['xhs_note', 'xhs_note_comment', 'xhs_creator']:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"\n{table}: {count} 条")

        # 显示最新的几条笔记
        if 'xhs_note' in tables:
            cursor.execute("""
                SELECT note_id, title, nickname, liked_count, collected_count, add_ts
                FROM xhs_note
                ORDER BY add_ts DESC
                LIMIT 5
            """)
            notes = cursor.fetchall()
            if notes:
                print("\n" + "=" * 50)
                print("最新笔记:")
                print("=" * 50)
                for note in notes:
                    print(f"  标题: {note[1][:30]}...")
                    print(f"  作者: {note[2]}")
                    print(f"  点赞: {note[3]}, 收藏: {note[4]}")
                    print(f"  ID: {note[0]}")
                    print("-" * 50)

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"错误: {e}")

if __name__ == '__main__':
    check_data()
