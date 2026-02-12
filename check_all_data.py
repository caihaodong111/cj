#!/usr/bin/env python3
"""查看所有平台的爬取数据"""
import pymysql

DB_CONFIG = {
    'host': '39.105.122.26',
    'port': 3306,
    'user': 'lxr',
    'password': 'lxr123123',
    'database': 'lxr'
}

# 平台表映射
PLATFORMS = {
    '小红书': ['xhs_note', 'xhs_note_comment', 'xhs_creator'],
    '抖音': ['douyin_aweme', 'douyin_aweme_comment', 'dy_creator'],
    'B站': ['bilibili_video', 'bilibili_video_comment', 'bilibili_up_info'],
    '快手': ['kuaishou_video', 'kuaishou_video_comment'],
    '微博': ['weibo_note', 'weibo_note_comment', 'weibo_creator'],
    '贴吧': ['tieba_note', 'tieba_comment', 'tieba_creator'],
    '知乎': ['zhihu_content', 'zhihu_comment', 'zhihu_creator'],
}

def check_all_data():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("=" * 60)
        print("                   全平台数据统计")
        print("=" * 60)

        # 获取所有表
        cursor.execute('SHOW TABLES')
        all_tables = [t[0] for t in cursor.fetchall()]

        total_notes = 0
        total_comments = 0

        for platform, tables in PLATFORMS.items():
            print(f"\n【{platform}】")

            for table in tables:
                if table in all_tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]

                    if count > 0:
                        if 'note' in table or 'video' in table or 'aweme' in table or 'content' in table:
                            total_notes += count
                            print(f"  📄 {table}: {count} 条")
                        elif 'comment' in table:
                            total_comments += count
                            print(f"  💬 {table}: {count} 条")
                        else:
                            print(f"  👤 {table}: {count} 条")
                else:
                    print(f"  ⚪ {table}: 表不存在")

        print("\n" + "=" * 60)
        print(f"总计: {total_notes} 条内容, {total_comments} 条评论")
        print("=" * 60)

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"错误: {e}")

if __name__ == '__main__':
    check_all_data()
