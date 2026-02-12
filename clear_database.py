#!/usr/bin/env python3
"""
清空 MySQL 数据库所有表
用法: python3 clear_database.py
"""

import pymysql

# 数据库配置
DB_CONFIG = {
    'host': '39.105.122.26',
    'port': 3306,
    'user': 'lxr',
    'password': 'lxr123123',
    'database': 'lxr'
}

def clear_database():
    try:
        print(f"正在连接数据库 {DB_CONFIG['host']}:{DB_CONFIG['port']}...")
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 获取所有表
        cursor.execute('SHOW TABLES')
        tables = cursor.fetchall()

        if not tables:
            print('数据库中没有表')
            return

        print(f'\n找到 {len(tables)} 个表:')
        for table in tables:
            print(f'  - {table[0]}')

        # 禁用外键检查
        cursor.execute('SET FOREIGN_KEY_CHECKS = 0')

        # 清空所有表
        for table in tables:
            table_name = table[0]
            cursor.execute(f'DROP TABLE IF EXISTS `{table_name}`')
            print(f'已删除表: {table_name}')

        # 启用外键检查
        cursor.execute('SET FOREIGN_KEY_CHECKS = 1')
        conn.commit()

        print(f'\n成功清空 {len(tables)} 个表')

        cursor.close()
        conn.close()

    except Exception as e:
        print(f'错误: {e}')

if __name__ == '__main__':
    clear_database()
